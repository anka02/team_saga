import argparse
import glob
import os
from pathlib import Path
import json
import time
import logging
import random
import re
from itertools import chain
from string import punctuation

import pandas as pd
import numpy as np

import torch
from torch.utils.data import Dataset, DataLoader, Subset
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger, WandbLogger
from datasets import load_dataset, load_metric
import datasets
import wandb


from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

# For more effective memory usage
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.enabled = True


def get_args_dict():
    args_dict = dict(
        model_name_or_path='t5-base',
        tokenizer_name_or_path='t5-base',
        max_seq_length=1024,
        learning_rate=3e-4,
        weight_decay=0.0,
        adam_epsilon=1e-8,
        warmup_steps=0,
        train_batch_size=8,
        eval_batch_size=8,
        num_train_epochs=1,
        gradient_accumulation_steps=1,
        n_gpu=0,
        max_grad_norm=1.0,
        freeze_embeds=False,
        freeze_encoder=True,
        logging=False
    )
    return argparse.Namespace(**args_dict)

class T5FineTuner(pl.LightningModule):
    def __init__(self, hparams):
        super(T5FineTuner, self).__init__()
        self.save_hyperparameters(hparams)
        self.model = T5ForConditionalGeneration.from_pretrained(hparams.model_name_or_path)
        self.tokenizer = T5Tokenizer.from_pretrained(hparams.tokenizer_name_or_path)
        self.rouge_metric = load_metric('rouge', keep_in_memory=True)

        if self.hparams.freeze_embeds:
            self.freeze_embeds()
        if self.hparams.freeze_encoder:
            self.freeze_params(self.model.get_encoder())


    def freeze_params(self, model):
        for par in model.parameters():
            par.requires_grad = False


    def freeze_embeds(self):
        """Freeze token embeddings and positional embeddings for bart, just token embeddings for t5."""
        try:
            self.freeze_params(self.model.model.shared)
            for d in [self.model.model.encoder, self.model.model.decoder]:
                self.freeze_params(d.embed_positions)
                self.freeze_params(d.embed_tokens)
        except AttributeError:
            self.freeze_params(self.model.shared)
            for d in [self.model.encoder, self.model.decoder]:
                self.freeze_params(d.embed_tokens)

    def lmap(self, f, x):
        """list(map(f, x))"""
        return list(map(f, x))


    def is_logger(self):
        return self.trainer.proc_rank <= 0

    def parse_score(self, result):
        return {k: round(v.mid.fmeasure * 100, 4) for k, v in result.items()}

    def forward(
            self, input_ids, attention_mask=None, decoder_input_ids=None, decoder_attention_mask=None, labels=None
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
        )

    def _step(self, batch):
        labels = batch["target_ids"]
        labels[labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            labels=labels,
            decoder_attention_mask=batch['target_mask']
        )

        loss = outputs[0]

        return loss


    def ids_to_clean_text(self, generated_ids):
        gen_text = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        return self.lmap(str.strip, gen_text)


    def _generative_step(self, batch) :

        t0 = time.time()

        generated_ids = self.model.generate(
            batch["source_ids"],
            attention_mask=batch["source_mask"],
            use_cache=True,
            decoder_attention_mask=batch['target_mask'],
            max_length=150,
            num_beams=2,
            repetition_penalty=2.5,
            length_penalty=1.0,
            early_stopping=True
        )
        preds = self.ids_to_clean_text(generated_ids)
        target = self.ids_to_clean_text(batch["target_ids"])

        gen_time = (time.time() - t0) / batch["source_ids"].shape[0]

        loss = self._step(batch)
        base_metrics = {'val_loss': loss}
        summ_len = np.mean(self.lmap(len, generated_ids))
        base_metrics.update(gen_time=gen_time, gen_len=summ_len, preds=preds, target=target)

        self.rouge_metric.add_batch(predictions=preds, references=target)

        return base_metrics


    def training_step(self, batch, batch_idx):
        loss = self._step(batch)

        if self.hparams.logging:
            self.log('train_loss', loss)
        return loss

    def training_epoch_end(self, outputs):
        avg_train_loss = torch.stack([x["loss"] for x in outputs]).mean()

        if self.hparams.logging:
            self.log('avg_train_loss', avg_train_loss, on_epoch=True, prog_bar=True)

    def validation_step(self, batch, batch_idx):
        return self._generative_step(batch)


    def validation_epoch_end(self, outputs):

        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()

        if self.hparams.logging:
            if self.hparams.n_gpu > 1:
                self.log('val_loss', avg_loss, on_epoch=True, prog_bar=True, sync_dist=True)
            else:
                self.log('val_loss', avg_loss, on_epoch=True, prog_bar=True)

        rouge_results = self.rouge_metric.compute()
        rouge_dict = self.parse_score(rouge_results)

        if self.hparams.logging:
            if self.hparams.n_gpu > 1:
                self.log_dict(rouge_dict, sync_dist=True)
            else:
                self.log_dict(rouge_dict)

        ## Clear out the lists for next epoch
        self.target_gen= []
        self.prediction_gen =[]
        return {"avg_val_loss": avg_loss,
                "rouge1" : rouge_results['rouge1'],
                "rougeL" : rouge_results['rougeL']}

    def test_step(self, batch, batch_idx):
        return self._generative_step(batch)


    def test_epoch_end(self, outputs):

        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()

        if self.hparams.logging:
            if self.hparams.n_gpu > 1:
                self.log('test_loss', avg_loss, on_epoch=True, prog_bar=True, sync_dist=True)
            else:
                self.log('test_loss', avg_loss, on_epoch=True, prog_bar=True)

        rouge_results = self.rouge_metric.compute()
        rouge_dict = self.parse_score(rouge_results)

        if self.hparams.logging:
            if self.hparams.n_gpu > 1:
                self.log_dict(rouge_dict, sync_dist=True)
            else:
                self.log_dict(rouge_dict)

        ## Clear out the lists for next epoch
        self.target_gen= []
        self.prediction_gen =[]
        return {"avg_val_loss": avg_loss,
                "rouge1" : rouge_results['rouge1'],
                "rougeL" : rouge_results['rougeL']}

    def configure_optimizers(self):
        "Prepare optimizer and schedule (linear warmup and decay)"

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)
        self.opt = optimizer
        return [optimizer]

    def optimizer_step(self,
                       epoch=None,
                       batch_idx=None,
                       optimizer=None,
                       optimizer_idx=None,
                       optimizer_closure=None,
                       on_tpu=None,
                       using_native_amp=None,
                       using_lbfgs=None):

        optimizer.step(closure=optimizer_closure)
        optimizer.zero_grad()
        self.lr_scheduler.step()

    def get_tqdm_dict(self):
        tqdm_dict = {"loss": "{:.3f}".format(self.trainer.avg_loss), "lr": self.lr_scheduler.get_last_lr()[-1]}

        return tqdm_dict