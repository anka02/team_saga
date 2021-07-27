# Covid Chatbot with text Summarization

## team_saga

This work is part of the Software Project: "Language Generation Tasks" at Saarland University, Summer Semester 2021.


# Overview

## About

This project implements a Chatbot using the `Rasa` open source library that is able to answer Covid-19 related questions and queries, such as case numbers in specified locations and travel restrictions and regulations in those locations. It is also capable of creating summarized information on selected topics and questions related to Covid, such as information about vaccines, Covid-19 symptoms and variants. The chatbot will indicate what kind of information it is capable of providing and will guide the user towards meaningful queries in the user interface.

Information about case numbers, restrictions and regulations is queried through an API in real time, ensuring up-to-date information retrieval. General information about Covid-19, such vaccine information is gathered through reputable major websites, such as the WHO. However, as information about Covid-19 is constantly being updated, based on the latest research and evidence, this information might not reflect the most up-to-date knowledge we have acquired about the Covid-19 pandemic. 

If you wish to try the Chatbot, you can find it in Telegram using the link `https://t.me/covid_19_chat_bot` 
or by searching in the Telegram App `@covid_19_chat_bot`.

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

There are two possibilities to run the Rasa based Chatbot:

On your localhost:

1. Please create and activate a virtual environment on your preferred location, e.g. using Anaconda `conda create --name myenv python=3.8`, WINDOWS: `activate myenv`, LINUX and MacOS `source activate`.
2. Install the required packages by `$ pip install -r requirements.txt` on your virtual environment. Make sure you also have `jupyter-notebook` installed on your virtual environment in case you want to run any of the notebooks, e.g. for further training.
3. Clone the repository. Download t5-checkpoint to nlg/checkpoints/ . You can find a selection of saved checkpoints from https://drive.google.com/drive/folders/1q2hrzzbo058B4c3NSG9bw5OwhA6P30Ig?usp=sharing
4. Setup Rasa: 
    If you prefer to run the Chatbot in shell, run shell-command `rasa train`, which trains a model 
    using the NLU data and stories and saves the trained model in `./models`. The Action Server needs to be started with the extra command `rasa run actions`.
    And then run `rasa run shell`. More Rasa commands could be found here: https://rasa.com/docs/rasa/command-line-interface/. 
    The deployment of Rasa X allows running training from the browser, which will open the window automatically on `http://localhost:5005/api`. By default Rasa X
    uses port `5005` on the `localhost`. Click the button `Train`, wait for the model creation and start a conversation.
The first deployment of Rasa Action Server takes about 5-10 minutes (depending on the capacity of the PC) to create the files,
needed for the summary part, the next deployment takes less than a minute.

In docker container:

1. Install Docker (if it isn't installed) https://docs.docker.com/engine/install/
2. Clone the repository. Download t5-checkpoint to nlg/checkpoints/ from https://drive.google.com/drive/folders/1q2hrzzbo058B4c3NSG9bw5OwhA6P30Ig?usp=sharing
3. run `docker-build.sh` and `docker-run.sh`. The building process takes about 9 mins and includes full installation. 
4. Open Rasa X in browser and type`localhost:5002/login?username=<displayed on the screen>` and in the left drop-out part of the page click `Train` to train the model
5. Open the generated link `Guest URL` displayed in the terminal : `http://localhost:5002/guest/conversations/productio/<genarated code>`.

The default docker deployment includes running Rasa X and opening the Chatbot UI. The configuration of the Chatbot UIs mode can be changed in the 
`entrypoint.sh` file. After making any changes in the configuration files, you need to rebuild the container.

# Models and Implementation

## Rasa

Rasa is an open-source machine learning framework for automated conversations. It is capable of interpreting messages, holding conversations and connecting to messaging channels and APIs.
The full project includes Rasa open source for training the NLU pipeline, integrating NLG into the Chatbot, Action Server for implementing custom actions and RASA X as a UI frontend.

To extract information from user messages the NLU pipeline should be able to recognize the user's intent and any entities their message contain. 
NLU training data consists of example user utterances categorized by intent. The data used in the NLU pipeline is stored in the `data` folder. Rasa uses a number of machine learning tools and models to extract entities and make predictions among other tasks as part of the NLU pipeline. The specific information is stored in the `config.yml` file and any specifications including languages and pipeline keys can be viewed and changed from there.

After receiving a message, the model will predict an action that the assistant should perform next. The Action Server is responsible for the performance of the next action.
A custom action provided in our chatbot uses an API call and query to fetch Covid-19 related information, which can be further summarized by the trained summarization model that is integrated into the chatbot. When your assistant predicts a custom action, the Rasa server sends a POST request to the action server
with a json payload including the name of the predicted action, the conversation ID, the contents of the tracker and the contents of the domain.
When the action server finishes running a custom action, it returns a json payload of responses and events. See the API specifications for details about the request and response payloads.
The Rasa server then returns the responses to the user and adds the events to the conversation tracker. The implementation of actions is stored in `actions/actions.py`
The design of the conversation, which assumes that the assistant is asking for specific information, is defined in forms.

Rasa x deploys the user interface and fine-tunes the NLU model through interactive learning. The Rasa X UI consists of layers built on top of Rasa Open Source.
Moreover, Rasa X can be connected to many popular messaging apps, such as Telegram, Facebook, Slack and  even custom applications. 
To try our Telegram chatbot go to the following URL: `https://t.me/covid_19_chat_bot` or search in your Telegram App `@covid_19_chat_bot`.

## Text-to-Text Transfer Transformer (T5)

## Data
The summarized Covid-19 information including general information about symptoms, vaccines, advice, etc. are queried from the official website of
 World Health Organization https://www.who.int/ and summarized by the T5 model before providing the information to the user.
 
### APIs
We use several APIs to query up-to-date Covid-19 information. These include:
* `https://covid-api.com/api/reports/total` (COVID-19 confirmed case numbers by country)
* `https://covid-api.thinklumo.com/data` (COVID-19 restrictions by country)
* `https://www.trackcorona.live/api/cities/` (COVID-19 confirmed case numbers by city)
 
`covid-api.com`, is based on public data by **Johns Hopkins CSSE** https://github.com/CSSEGISandData/COVID-19.
The regulations, travel advisories, and travel restrictions are provided by Lumo's COVID-19 API, which uses IATA airport codes for fetching the location.

The API requests don't require any authentication, except `thinklumo`, where registration is required to get the API key. 
More information can be found on: https://developer.thinklumo.com.

### CNN/Daily Mail summarization dataset

# Experiments

# Results

# References
