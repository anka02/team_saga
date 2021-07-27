# Covid Chatbot with text Summarization

## team_saga

This work is part of the Software Project: "Language Generation Tasks" at Saarland University, Summer Semester 2021.


# Overview

## About

This project implements a Chatbot using the `Rasa` open source library that is able to answer Covid-19 related questions and queries, such as case numbers in specified locations and travel restrictions and regulations in those locations. It is also capable of creating summarized information on selected topics and questions related to Covid, such as information about vaccines, Covid-19 symptoms and variants. The chatbot will indicate what kind of information it is capable of providing and will guide the user towards meaningful queries in the user interface.

Information about case numbers, restrictions and regulations is queried through an API in real time, ensuring up-to-date information retrieval. General information about Covid-19, such vaccine information is gathered through reputable major websites, such as the WHO. However, as information about Covid-19 is constantly being updated, based on the latest research and evidence, this information might not reflect the most up-to-date knowledge we have acquired about the Covid-19 pandemic. 

If you would like to try, you can find our Chatbot in Telegram using the link `https://t.me/covid_19_chat_bot` 
or search in App `@covid_19_chat_bot`.

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

There are two possibilities to run Rasa Chatbot:

On your localhost:

1. Please create and activate a virtual environment on your preferred location, e.g. using Anaconda `conda create --name myenv python=3.8`, WINDOWS: `activate myenv`, LINUX and MacOS `source activate`.
2. Install the required packages by `$ pip install -r requirements.txt` on your virtual environment. Make sure you also have `jupyter-notebook` installed on your virtual environment in case you want to run any of the notebooks, e.g. for further training.
3. Clone the repository. Download t5-checkpoint to nlg/checkpoints/ . You can find a selection of saved checkpoints from https://drive.google.com/drive/folders/1q2hrzzbo058B4c3NSG9bw5OwhA6P30Ig?usp=sharing
4. Setup Rasa: 
    If you prefer to run Chatbot in shell, run shell-command `rasa train`, which trains a model 
    using the NLU data and stories, saves trained model in `./models`. The Action Server need to be started with the extra command `rasa run actions`.
    And then run `rasa run shell`. More Rasa commands could be found here: https://rasa.com/docs/rasa/command-line-interface/. 
    The deployment of Rasa X allows running training from the browser, which will be open the window automatically on `http://localhost:5005/api`. By default Rasa X
    use port `5005` on the `localhost`. Click the button `Train`, wait for the model creation and start a conversation.
The first deployment of Rasa Action Server takes about 5-10 minutes (depending on the capacity of the PC) to create the files,
needed for the summary part, the next deployment takes less than a minute.

In docker container:

1. Install Docker (if it isn't installed) https://docs.docker.com/engine/install/
2. Clone the repository. Download t5-checkpoint to nlg/checkpoints/ . *WE NEED TO UPLOAD IT SOMEWHERE, TO ALLOW OTHER ACCESS TO THE MODEL*
3. run `docker-build.sh` and `docker-run.sh`. The building process takes about 9 mins and included full installation. 
4. Open Rasa X to train the model for use in NLU part in browser `https://localhost:5002` and then open generated the link `Guest URL` displayed in the terminal 
`http://localhost:5002/guest/conversations/productio/<genarated code>`.
    Alternative: download the model from *WE NEED TO UPLOAD IT SOMEWHERE, TO ALLOW OTHERS ACCESS TO THE MODEL* to models/ and then run generated the link `Guest URL`

The default docker deployment includes running Rasa X and opens UI Chatbot mode. The configuration of Chatbot's mode could be changed in 
`entrypoint.sh`. After any changes in configuration files, you need to rebuild the container.

# Models and Implementation

## Rasa

Rasa is an open-source machine learning framework for automated conversations. Understand messages, hold conversations, and connect to messaging channels and APIs.
The full project includes RASA Open Source for training NLU and providing NLG part, Action Server for implementing custom actions and RASA X as UI frontend.

To extract information from user messages NLU should be able to recognize the user's intent and any entities their message contains. 
NLU training data consists of example user utterances categorized by intent. The date uses in NLU is stored in `data`. To extract the entities and make NLU predictions was used an ML model,
the specification that contains the language and pipeline keys. This information is stored in `config.yml` file. 

After the message, the model will predict an action that the assistant should perform next. The Action Server is responsible for the performance of the next action.
A custom action provides in our chat-bot uses an API call and query the summarized texts. When your assistant predicts a custom action, the Rasa server sends a POST request to the action server
with a json payload including the name of the predicted action, the conversation ID, the contents of the tracker and the contents of the domain.
When the action server finishes running a custom action, it returns a json payload of responses and events. See the API spec for details about the request and response payloads.
The Rasa server then returns the responses to the user and adds the events to the conversation tracker. The implementation of actions stored in `actions/actions.py`
The specific design of the conversation, which assumes that the assistant is asking for specific information, as set out in forms.

Rasa x deploys the user interface and fine-tunes the NLU model through interactive learning. Rasa X are layers built on top of Rasa Open Source.
Moreover, Rasa can use different connectors such that Telegram, Facebook, Slack and custom ones. 
Try Telegram chatbot run: `https://t.me/covid_19_chat_bot` or search in your Telegram App `@covid_19_chat_bot`.

## Text-to-Text Transfer Transformer (T5)

## Data
The general information about Covid-19, vaccines, advice and more other retrieves from the official website of
 World Health Organization https://www.who.int/ and uses for summarization task.
### APIs
Used APIs:
* `https://covid-api.com/api/reports/total` (Retrieve the information about COVID-19 numbers by country)
* `https://covid-api.thinklumo.com/data` (Retrieve the information about COVID-19 restrictions by country)
* `https://www.trackcorona.live/api/cities/` (Retrieve the information about COVID-19 numbers by city)
 
Retrieving the information about Covid-19 situation in the specific country or german region provided `covid-api.com`, that 
based on public data by **Johns Hopkins CSSE** https://github.com/CSSEGISandData/COVID-19.
The regulations requests Lumo's COVID-19 API,which provides coronavirus, travel advisories, and travel restrictions for the country uses IATA airport code.

The API requests don't require any authentication, except `thinklumo`.  
Use of the last one is free, but registration is required to get API key, more information https://developer.thinklumo.com.

### CNN/Daily Mail summarization dataset

# Experiments

# Results

# References
