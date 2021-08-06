# Covid Chatbot with text Summarization

## team_saga

This work is part of the Software Project: "Language Generation Tasks" at Saarland University, Summer Semester 2021.


# Overview

## About

This project implements a Chatbot using the `Rasa` open source library that is able to answer Covid-19 related questions and queries, such as case numbers in specified locations and travel restrictions and regulations in those locations. It is also capable of creating summarized information on selected topics and questions related to Covid, such as information about vaccines, Covid-19 symptoms and variants. The chatbot will indicate what kind of information it is capable of providing and will guide the user towards meaningful queries in the user interface.

Information about case numbers, restrictions and regulations is queried through an API in real time, ensuring up-to-date information retrieval. General information about Covid-19, such vaccine information is gathered through reputable major websites, such as the WHO. However, as information about Covid-19 is constantly being updated, based on the latest research and evidence, this information might not reflect the most up-to-date knowledge we have acquired about the Covid-19 pandemic. 

If you wish to try the Chatbot, you can find it in Telegram using the link `https://t.me/covid_19_chat_bot` 
or by searching `@covid_19_chat_bot` in the Telegram App. The chatbot is called `Covid Chatbot(LGT)`.

## Requirements

* The scripts and notebooks were tested on Python 3.8 for Mac OS and Windows and Linux.
* See the **requirements-docker.txt** files for more details on the required packages.
* Using a virtual environment is highly recommended. We used Anaconda.

* The summarization model is already fine-tuned for our task and **does not need training**.
 * A saved checkpoint can be found from https://drive.google.com/drive/folders/1q2hrzzbo058B4c3NSG9bw5OwhA6P30Ig?usp=sharing
* However, it is possible to train the model further using the provided notebooks in the **nlg** folder. 
* GPU is necessary for training the summarization model, but not strictly necessary for running the chatbot.
* Average training time for the summarization model ranges from 10-12 hours per epoch, using 4 Geforce GTX Titan GPUs, with 12gb of allocated GPU memory each. Consider a maximum batch size of 8 to avoid memory errors on Cuda.

## Instructions

There are two possibilities to run the Rasa based Chatbot:

On your localhost:

1. Please create and activate a virtual environment in your preferred location, e.g. using Anaconda first run `conda create --name myenv python=3.8`,then depending on the system WINDOWS: `activate myenv`, LINUX and MacOS `conda activate myenv`.
2. Clone the repository. Download t5-checkpoint to nlg/checkpoints/. You can find a saved checkpoint in a format that PyTorch can process from https://drive.google.com/drive/folders/1q2hrzzbo058B4c3NSG9bw5OwhA6P30Ig?usp=sharing Please don't try to unzip the file.
3. Install the required packages by `$ pip install -r requirements-docker.txt` on your virtual environment. The installation of Rasa X UI could be proceeded just maually. Please run in terminal: `pip3 install rasa-x --extra-index-url https://pypi.rasa.com/simple` 
or follow instructions here https://rasa.com/docs/rasa-x/installation-and-setup/install/local-mode. 
Make sure you also have `jupyter-notebook` installed in your virtual environment in case you want to run any of the notebooks, e.g. for further training. 
4. Setup Rasa: 
    If you prefer to run the Chatbot in shell, run shell-command `rasa train`, which trains a model 
    using the Natural Language Understanding (NLU) data and stories and saves the trained model in `./models`. The Action Server needs to be started with the extra command `rasa run actions` (in other terminal with activated virtual environment).
    And then run `rasa shell` to open Chatbot in shell or `rasa x` to open it in browser with UI. More Rasa commands could be found here: https://rasa.com/docs/rasa/command-line-interface/. 
    The deployment of Rasa X allows running training and configuring the data from the browser, which will open the window automatically on `http://localhost:5005/api` . Please select the `Model` field and click the arrow `Up` to activate the model or click `Train` to train the model and then activate it. Now you are done and conversation could be started in the field `Talk to your bot`. By default Rasa X uses port `5005` on the `localhost`. You can also open the Chatbot in production mode by following the way: `Conersation`,`Share your bot` and open the generated link in another browser window.

The first deployment of Rasa Action Server takes about 5-10 minutes (depending on the capacity of the PC) to create the files,
needed for the summary part, the next deployment takes less than a minute.

In docker container:

1. Install Docker (if it isn't installed) https://docs.docker.com/engine/install/
2. Please create and activate a virtual environment in your preferred location, e.g. using Anaconda first run `conda create --name myenv python=3.8`,then depending on the system WINDOWS: `activate myenv`, LINUX and MacOS `conda activate myenv`.
3. Clone the repository. Download t5-checkpoint to nlg/checkpoints/ from https://drive.google.com/drive/folders/1q2hrzzbo058B4c3NSG9bw5OwhA6P30Ig?usp=sharing. Please don't try to unzip the file.
4. run `docker-build.sh` to create docker container. The building process takes about 9 mins and includes full installation. (Note :  On WINDOWS this Docker container should be configured and running under WSL2.)
5. run `docker-run.sh` to run docker container.
6. Open Rasa X in browser and type`localhost:5002/login?username=<displayed on the screen>` and in the left drop-out part of the page click `Train` to train the model.Then select the `Model` field and click the arrow `Up` to activate the model.
7. Open the generated link `Guest URL` displayed in the terminal : `http://localhost:5002/guest/conversations/production/<genarated code>`.

The default docker deployment includes running Rasa X and opening the Chatbot UI. The configuration of the Chatbot UIs mode can be changed in the 
`entrypoint.sh` file. After making any changes in the configuration files, you need to rebuild the container.

# Models and Implementation

## Rasa

Rasa is an open-source machine learning framework for automated conversations. It is capable of interpreting messages, holding conversations and connecting to messaging channels and APIs.
The full project includes Rasa open source for training the NLU pipeline, integrating Natural Language Generation (NLG) into the Chatbot, Action Server for implementing custom actions and RASA X as a UI frontend. For more information consult `https://rasa.com/docs/`.

## Text-to-Text Transfer Transformer (T5)

We use a Text-to-Text Transfer Transformer (T5) ([Raffel et al., 2020](https://arxiv.org/pdf/1910.10683.pdf)) model for our summarization task. It closely follows the Transformer architecture introduced by [Vaswani et al. (2017)](https://arxiv.org/pdf/1706.03762.pdf) and can be described as an Encoder-Decoder Transformer model.

The pretrained T5 model that we fine-tune for our summarization task can be found from https://huggingface.co/transformers/model_doc/t5.html#t5config and is avaiable through the `HuggingFace Transformers` python library (`pip install transformers`).

## Data
The summarized Covid-19 information including general information about symptoms, vaccines, advice, etc. are queried from the official website of
 World Health Organization https://www.who.int/ and summarized by the T5 model before providing the information to the user.
 
### REST APIs
We use several REST APIs to query up-to-date Covid-19 information. These include:
* `https://covid-api.com/api/reports/total` (COVID-19 confirmed case numbers by country)
* `https://covid-api.thinklumo.com/data` (COVID-19 restrictions by country)
* `https://www.trackcorona.live/api/cities/` (COVID-19 confirmed case numbers by city)
 
`covid-api.com`, is based on public data by **Johns Hopkins CSSE** https://github.com/CSSEGISandData/COVID-19.
The regulations, travel advisories, and travel restrictions are provided by Lumo's COVID-19 API, which uses IATA airport codes for fetching the location.

The API requests don't require any authentication, except `thinklumo`, where registration is required to get the API key. 
More information can be found on: https://developer.thinklumo.com.

### CNN/Daily Mail summarization dataset

Our T5 summarization model was fine-tuned using the CNN / Daily Mail dataset, which consists of news articles crawled from the CNN and Daily Mail websites over a long period of time and human annotated abstractive summaries of those news articles. Even though our training data is not related to Covid-19, the domains of online news articles and online Covid-19 articles / information are close enough stylistically and structurally (in terms of the text) to allow the model to find relevant pieces of information that can be included in the generated summaries.

The dataset can be found from https://huggingface.co/datasets/cnn_dailymail and it can be accesed using the `datasets` python library. (`pip install datasets`)

We apply simple filters to this dataset to remove articles and summaries that are either too long or too short to be representative training examples for
our task. For further information consult `nlg/t5-fine-tuning.ipynb`.

After filtering out unwanted entries the dataset consists of

* 237,714 training pairs
* 11,188 validation pairs
* 9532 test pairs

# Chatbot system and UI

To extract information from user messages the NLU pipeline should be able to recognize the user's intent and any entities their message contain. 
NLU training data consists of example user utterances categorized by intent. The data used in the NLU pipeline is stored in the `data` folder. Rasa uses a number of machine learning tools and models to extract entities and make predictions among other tasks as part of the NLU pipeline. The specific information is stored in the `config.yml` file and any specifications including languages and pipeline keys can be viewed and changed from there.

After receiving a message, the model will predict an action that the assistant should perform next. The Action Server is responsible for the performance of the next action.
A custom action provided in our chatbot uses an API call and query to fetch Covid-19 related information, which can be further summarized by the trained summarization model that is integrated into the chatbot. When your assistant predicts a custom action, the Rasa server sends a POST request to the action server
with a JSON payload including the name of the predicted action, the conversation ID, the contents of the tracker and the contents of the domain.
When the action server finishes running a custom action, it returns a json payload of responses and events. See section `APIs` for details about the request and response payloads.
The Rasa server then returns the responses to the user and adds the events to the conversation tracker. The implementation of actions is stored in `actions/actions.py`
The design of the conversation, which assumes that the assistant is asking for specific information, is defined in forms.

Rasa X deploys the user interface and fine-tunes the NLU model through interactive learning. The Rasa X UI consists of layers built on top of Rasa Open Source.
Moreover, Rasa X can be connected to many popular messaging apps, such as Telegram, Facebook, Slack and  even custom applications. 
To try our Telegram chatbot go to the following URL: `https://t.me/covid_19_chat_bot` or search in your Telegram App `@covid_19_chat_bot`.

# Experiments

In order to assess our summarization model we fine-tune the T5 model by using the CNN / Daily Mail dataset. We use the Rouge score (Lin, 2004) metric to evaluate the performance of our model.

We experiment with 4 different conditions.

1. We fine-tune the whole model.
2. We freeze the weights in the encoder layer and the in the embeddings.
3. We only freeze the encoder layer weights.
4. We only freeze the embedding layer weights.

We fine-tune the model for a total of 5 epochs for each condition. Overall, we acquire the best performing model by fine-tunng the whole model. However, the model also shows signs of over-fitting very quicky and we acquire the highest scores by fine-tunng it only 1 epoch, whereafter the performance only decreases.

# Results

Here we summarize our evaluation results. We report the highest Rouge scores from each condition, where the model was trained overall for 5 epochs.

| Condition             | Rouge-1    | Rouge-2   | Rouge-L    |
| ----------------------| -----------|-----------|------------|
| Full-model (1)        | **42.44**  | **20.61** | **30.44**  |
| Freeze both (2)       | 41.29      | 19.56     | 29.39      | 
| Freeze encoder (3)    | 41.74      | 19.97     | 29.81      | 
| Freeze embeddings (4) | 42.06      | 20.33     | 30.31      |

The main finding here is that freezing the weights is not beneficial for the task. Freezing the embeddings has a smaller effect on performance than freezing the encoder. Regardless, The more layers we freeze, the lower the scores we achieve, even when we fine-tune the model longer. 

# References

Chin-Yew Lin. 2004.  Rouge: A package for automaticevaluation of summaries. In ACL 2004.

Colin Raffel, Noam M. Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, W. Li, and Peter J. Liu. 2020. Exploring the limits of transfer learning with a unified text-to-text transformer. ArXiv, abs/1910.10683.

Ashish Vaswani, Noam M. Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. 2017. Attention is all you need. ArXiv, abs/1706.03762.
