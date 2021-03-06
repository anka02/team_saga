from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen, Request
from collections import defaultdict
import pprint
import re
import json
import os

DICT_FOR_SUMM_PATH = os.path.join(os.path.dirname(__file__),'dict_for_summarization.json')

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

# As discussed previously, the dictionary was created with current information from the website.
# However it took some time for creation and others it could be dowloded and created directly with
# running server and every night probably be reloaded, it could make the program faster. And not
# create the whole dictionary every time but take from the updated json file.

def create_dict_for_summarization():

    dict_summarization = defaultdict(dict)
    headers= {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}

    reg_url_vaccine_general = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/covid-19-vaccines/advice'
    req_vaccine_general = Request(url=reg_url_vaccine_general, headers=headers)
    html_vaccine_general = urlopen(req_vaccine_general).read()
    vaccine_general_info = " ".join(text_from_html(html_vaccine_general).split()[398:-250])
    dict_summarization['vaccine']['vaccine_general_info'] = [vaccine_general_info, reg_url_vaccine_general]

    reg_url_az = 'https://www.who.int/news-room/feature-stories/detail/the-oxford-astrazeneca-covid-19-vaccine-what-you-need-to-know'
    req_az = Request(url=reg_url_az, headers=headers)
    html_az = urlopen(req_az).read()
    az_vaccine = " ".join(text_from_html(html_az).split()[496:1202])
    dict_summarization['vaccine']['az_vaccine'] = [az_vaccine,reg_url_az]

    reg_url_mod = 'https://www.who.int/news-room/feature-stories/detail/the-moderna-covid-19-mrna-1273-vaccine-what-you-need-to-know'
    req_mod = Request(url=reg_url_mod, headers=headers)
    html_mod = urlopen(req_mod).read()
    moderna_vaccine = " ".join(text_from_html(html_mod).split()[427:1259])
    dict_summarization['vaccine']['moderna_vaccine'] = [moderna_vaccine , reg_url_mod]

    reg_url_bio = 'https://www.who.int/news-room/feature-stories/detail/who-can-take-the-pfizer-biontech-covid-19--vaccine'
    req_bio = Request(url=reg_url_bio, headers=headers)
    html_bio = urlopen(req_bio).read()
    biontech_vaccine = " ".join(text_from_html(html_bio).split()[456:1488])
    dict_summarization['vaccine']['biontech_vaccine'] = [biontech_vaccine ,reg_url_bio]

    reg_url_sinopharm = 'https://www.who.int/news-room/feature-stories/detail/the-sinopharm-covid-19-vaccine-what-you-need-to-know'
    req_sinopharm = Request(url=reg_url_sinopharm, headers=headers)
    html_sinopharm = urlopen(req_sinopharm).read()
    sinopharm_vaccine = " ".join(text_from_html(html_sinopharm).split()[459:1360])
    dict_summarization['vaccine']['sinopharm_vaccine'] = [sinopharm_vaccine ,reg_url_sinopharm]

    reg_url_sinovac = 'https://www.who.int/news-room/feature-stories/detail/the-sinovac-covid-19-vaccine-what-you-need-to-know'
    req_sinovac = Request(url=reg_url_sinovac, headers=headers)
    html_sinovac = urlopen(req_sinovac).read()
    sinovac_vaccine = " ".join(text_from_html(html_sinovac).split()[436:1479])
    dict_summarization['vaccine']['sinovac_vaccine'] = [sinovac_vaccine , reg_url_sinovac]

    reg_url_cov_overview = 'https://www.who.int/health-topics/coronavirus#tab=tab_1'
    req_cov_overview = Request(url=reg_url_cov_overview, headers=headers)
    html_cov_overview = urlopen(req_cov_overview).read()
    covid_overview = " ".join(text_from_html(html_cov_overview).split()[370:-592])
    dict_summarization['covid_overview'] = [covid_overview ,reg_url_cov_overview]

    reg_url_symptome = 'https://www.who.int/health-topics/coronavirus#tab=tab_3'
    req_symptome = Request(url=reg_url_symptome, headers=headers)
    html_symptome = urlopen(req_symptome).read()
    symptoms = " ".join(text_from_html(html_symptome).split()[623:-356])
    dict_summarization['symptoms'] = [symptoms ,reg_url_symptome]

    reg_url_cov_variants = 'https://www.who.int/en/activities/tracking-SARS-CoV-2-variants/'
    req_cov_variants = Request(url=reg_url_cov_variants, headers=headers)
    html_cov_variants = urlopen(req_cov_variants).read()
    covid_variants = " ".join(text_from_html(html_cov_variants).split()[358:-370])
    dict_summarization['covid-variants'] = [covid_variants ,reg_url_cov_variants]

    reg_url_QA = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/question-and-answers-hub/q-a-detail/coronavirus-disease-covid-19'
    req_QA = Request(url=reg_url_QA, headers=headers)
    html_QA = urlopen(req_QA).read()
    parsed_html_QA = BeautifulSoup(html_QA, "html.parser")
    for elems in parsed_html_QA.find_all('div', attrs={'class': 'sf-accordion__panel'}):
        questions = elems.find('div', attrs={'class': 'sf-accordion__trigger-panel'}).text
        answers = elems.find('div', attrs={'class': 'sf-accordion__content'}).text
        questions = re.sub(r'\s+', ' ', questions)
        answers = re.sub(r'\s+', ' ', answers)

        if questions.strip() == "How can we protect others and ourselves if we don't know who is infected?":
            dict_summarization["How can we protect others?"] = [answers.strip() , reg_url_QA]
        if questions.strip() == "What test should I get to see if I have COVID-19?":
            dict_summarization["What test should I get if I have COVID-19?"] = [answers.strip() , reg_url_QA]
        if len(questions.strip()) <= 46:
            dict_summarization[questions.strip()] = [answers.strip() , reg_url_QA]
        else:
            dict_summarization[questions.strip()[:45]] = [answers.strip(), reg_url_QA]

    return dict_summarization

def write_dictionary(dictionary=None):
    with open(DICT_FOR_SUMM_PATH, 'w') as fp:
        if dictionary is None:
            json.dump(create_dict_for_summarization(), fp, ensure_ascii=False, indent=4, sort_keys=True)
        else:
            json.dump(dictionary,fp)



# def search_info(entities,dictionary_from_text=None): #must be list of strngs
#     if dictionary_from_text is None:
#         with open(DICT_FOR_SUMM_PATH) as jsonFile:
#             dictionary_from_text = json.load(jsonFile)
#     if entities[0] == 'vaccine':
#         return dictionary_from_text[entities[0]][entities[1]]
#     return dictionary_from_text[entities[0]]

def main():
    write_dictionary()
    with open("dict_for_summarization.json") as jsonFile:
        created_dict = json.load(jsonFile)
    # PrettyJson = json.dumps(created_dict, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
    # print("Displaying Pretty Printed JSON Data")
    # print(PrettyJson)
    # print(created_dict['covid-variants'][0])
    #
    # print(created_dict['vaccine']['sinovac_vaccine'][0])
    # print(create_dict_for_summarization())


if __name__ == "__main__":
    main()
