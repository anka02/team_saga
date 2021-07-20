# Covid Chatbot with text Summarization

## team_saga

This work is part of the Software Project: "Language Generation Tasks" at Saarland University, Summer Semester 2021.


# Overview

## About

This project implements a Chatbot using the `Rasa` open source library that is able to answer Covid-19 related questions and queries, such as case numbers in specified locations and travel restrictions and regulations in those locations. It is also capable of creating summarized information on selected topics and questions related to Covid, such as information about vaccines, Covid-19 symptoms and variants. The chatbot will indicate what kind of information it is capable of providing and will guide the user towards meaningful queries in the user interface.

Information about case numbers, restrictions and regulations is queried through an API in real time, ensuring up-to-date information retrieval. General information about Covid-19, such vaccine information is gathered through reputable major websites, such as the WHO. However, as information about Covid-19 is constantly being updated, based on the latest research and evidence, this information might not reflect the most up-to-date knowledge we have acquired about the Covid-19 pandemic.

## Requirements

* The scripts and notebooks were tested on Python 3.7 for Linux and 3.8 for Mac OS and Windows.
  * At the time of testing, `Rasa` python package does not yet support Python 3.8 on Linux.
* See the **requirements.txt** files for more details on the required packages.
* Using a virtual environment is highly recommended. We used Anaconda.

* The summarization model is already fine-tuned for our task and **does not need training**.
* However, it is possible to train the model further using the provided notebooks in the **nlg** folder. 
* GPU is necessary for training the summarization model, but not strictly necessary for running the chatbot on RASA.
* Average training time for the summarization model ranges from 10-12 hours per epoch, using 4 Geforce GTX Titan GPUs, with 12gb of allocated GPU memory each. Consider a maximum batch size of 8 to avoid memory errors on Cuda.

## Instructions

1. Please create a virtual environment on your preferred location, e.g. using Anaconda, and install the required packages by `$ pip install -r requirements.txt` on your virtual environment. Make sure you also have `jupyter-notebook` installed on your virtual environment in case you want to run any of the notebooks, e.g. for further training.
2. Clone the repository.
3. Setup Rasa...

# Models and Implementation

## Rasa

## Text-to-Text Transfer Transformer (T5)

## Data

### APIs

### CNN/Daily Mail summarization dataset

# Experiments

# Results

# References
