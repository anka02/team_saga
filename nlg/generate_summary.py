import argparse
import glob
import os
from pathlib import Path
import json
import random
import re
from itertools import chain
from string import punctuation

import pandas as pd
import numpy as np

import torch
import pytorch_lightning as pl



from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer
)

from model_config import T5FineTuner, get_args_dict

# For more effective memory usage
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.enabled = True

# resolve current directory
try:
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    print('__file__ does not exist for notebook, use current directory instead')
    FILE_DIR = Path().resolve()

CKPT_DIR = os.path.join(FILE_DIR, 'checkpoints')
CKPT_NAME = 'frozen_epoch=0.ckpt'

# intialize tokenizer and model
tokenizer = T5Tokenizer.from_pretrained('t5-base')
args_dict = get_args_dict()
model = T5FineTuner(args_dict)

# Load checkpoint
ckpt_path = os.path.join(CKPT_DIR, CKPT_NAME)
checkpoint = torch.load(ckpt_path, map_location=lambda storage, loc: storage)
model.load_state_dict(checkpoint['state_dict'])

# Functions for text generation
def clean_text(text):
    text = text.replace('\n', '')
    text = text.replace('``', '')
    text = text.replace('"', '')
    return text

def encode_input(text, tokenizer):
    input = clean_text(text)
    source = tokenizer.batch_encode_plus([input], max_length=1024,
                                              padding='max_length', truncation=True, return_tensors="pt")

    source_ids = source["input_ids"]
    src_mask = source["attention_mask"]

    return {"source_ids": source_ids, "source_mask": src_mask}


def summarize(input, model, tokenizer):

    # check input is the right format
    if not isinstance(input, str):
        raise TypeError('Expected a string object, got ', type(input))

    source = encode_input(input, tokenizer)

    generated_ids = model.model.generate(
        source["source_ids"],
        attention_mask=source["source_mask"],
        use_cache=True,
        max_length=250,
        num_beams=2,
        repetition_penalty=2.5,
        length_penalty=1.0,
        early_stopping=True
    )
    preds = model.ids_to_clean_text(generated_ids)

    return preds


# test
with open("./Texts/covid-19_variants.txt", "r", encoding="utf-8") as f:
    example_text = f.read()

pred = summarize(example_text, model, tokenizer)

print(pred)






