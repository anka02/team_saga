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
import pprint
import torch
import pytorch_lightning as pl
import re

try:
    from .create_summarization_dict import create_dict_for_summarization
except ImportError:
    from create_summarization_dict import create_dict_for_summarization
from _collections import defaultdict

from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer
)

try:
    from .model_config import T5FineTuner, get_args_dict
except ImportError:
    from model_config import T5FineTuner, get_args_dict

# For more effective memory usage
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.enabled = True
'''with open("dict_for_summarization.json") as jsonFile:
    dictionary_for_summarization = json.load(jsonFile)'''
DICTIONARY_FOR_SUMMARIZATION = create_dict_for_summarization()
DICT_SUM_PATH = os.path.join(os.path.dirname(__file__),'summarized_dict.json')

# resolve current directory
try:
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    print('__file__ does not exist for notebook, use current directory instead')
    FILE_DIR = Path().resolve()

CKPT_DIR = os.path.join(FILE_DIR, 'checkpoints')
CKPT_NAME = 'best_checkpoint.ckpt'

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


def do_summarization_in_dict(dictionary_for_summarization):
    summarized_dictionary = defaultdict(dict)
    for k,v in dictionary_for_summarization.items():
        if k == 'vaccine':
            for vaccine_name,info in dictionary_for_summarization['vaccine'].items():
                summarized_dictionary['vaccine'][vaccine_name] = summarize(info[0], model, tokenizer)
                # Add link to summarized info
                summarized_dictionary['vaccine'][vaccine_name].append(info[1])
        else:
            summarized_dictionary[k] = summarize(v[0], model, tokenizer)
            # Add link to summarized info
            summarized_dictionary[k].append(v[1])

    return summarized_dictionary


def write_in_dict(dictionary=None):
    with open(DICT_SUM_PATH, 'w') as fp:
        if dictionary is None:
            json.dump(do_summarization_in_dict(DICTIONARY_FOR_SUMMARIZATION), fp,ensure_ascii=False, indent=4, sort_keys=True)
        else:
            json.dump(dictionary,fp,ensure_ascii=False, indent=4, sort_keys=True)


def main():
    write_in_dict()

    # I've added it to print in nice readable way
    # and after summarization

    # with open ('summarized_dict.json') as jsonFile:
    #     created_dict = json.load(jsonFile)
    # PrettyJson = json.dumps(created_dict, indent=4, separators=(',', ': '), sort_keys=True)
    # print("Displaying Pretty Printed JSON Data")
    # print(PrettyJson)
    #print(created_dict)

if __name__ == '__main__':
    main()





