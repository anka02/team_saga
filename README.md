# Covid Chatbot with text Summarization

## team_saga

This work is part of the Software Project: "Language Generation Tasks" at Saarland University, Summer Semester 2021.


# Overview

## About

## Requirements

* The scripts and notebooks were tested on Python 3.7 for Linux and 3.8 for Mac OS and Windows.
  * At the time of testing, RASA python package does not yet support Python 3.8 on Linux.
* See the **requirements.txt** files for more details on the required packages.
* Using a virtual environment is highly recommended. We used Anaconda.

* The summarization model is already fine-tuned for our task and does not need training.
* However, it is possible to train the model further using the provided notebooks in the **nlg** folder. 
* GPU is necessary for training the summarization model, but not strictly necessary for running the chatbot on RASA.
* Average training time for the summarization model ranges from 10-12 hours per epoch, using 4 Geforce GTX Titan GPUs, with 12gb of allocated GPU memory each. Consider a maximum batch size of 8 to avoid memory errors on Cuda.

## Instructions

# Models and Implementation

## RASA

## Text-to-Text Transfer Transformer (T5)

## Data

### APIs

### CNN/Daily Mail summarization dataset

# Experiments

# Results

# References
