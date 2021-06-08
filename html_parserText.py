from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen, Request
import pprint

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

def create_txt(textdata,txt_name):
    with open(txt_name, mode="w+", encoding ="utf-8") as f:
        f.write(textdata)



headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
reg_url = 'https://www.who.int/news-room/feature-stories/detail/the-oxford-astrazeneca-covid-19-vaccine-what-you-need-to-know'
req = Request(url=reg_url, headers=headers)
html = urlopen(req).read()
#pp = pprint.PrettyPrinter(indent=4)
create_txt(" ".join(text_from_html(html).split()[507:1262]), "AZ-vaccine.txt")


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
reg_url = 'https://www.who.int/news-room/feature-stories/detail/the-moderna-covid-19-mrna-1273-vaccine-what-you-need-to-know'
req = Request(url=reg_url, headers=headers)
html = urlopen(req).read()
#pp = pprint.PrettyPrinter(indent=4)
create_txt(" ".join(text_from_html(html).split()[429:1262]), "Moderna-vaccine.txt")


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
reg_url = 'https://www.who.int/news-room/feature-stories/detail/who-can-take-the-pfizer-biontech-covid-19--vaccine'
req = Request(url=reg_url, headers=headers)
html = urlopen(req).read()
#pp = pprint.PrettyPrinter(indent=4)
create_txt(" ".join(text_from_html(html).split()[459:1262]), "Biontech-vaccine.txt")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
reg_url = 'https://www.who.int/news-room/feature-stories/detail/the-sinopharm-covid-19-vaccine-what-you-need-to-know'
req = Request(url=reg_url, headers=headers)
html = urlopen(req).read()
#pp = pprint.PrettyPrinter(indent=4)
create_txt(" ".join(text_from_html(html).split()[470:1262]), "Sinopharm-vaccine.txt")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
reg_url = 'https://www.who.int/news-room/feature-stories/detail/the-sinovac-covid-19-vaccine-what-you-need-to-know'
req = Request(url=reg_url, headers=headers)
html = urlopen(req).read()
#pp = pprint.PrettyPrinter(indent=4)
create_txt(" ".join(text_from_html(html).split()[447:1262]), "Sinovac-vaccine.txt")

# print("SWEDEN")
# html_1 = urllib.request.urlopen('https://se.usembassy.gov/covid-19-coronavirus-information/').read()
# pp.pprint(text_from_html(html_1))
#
# print("ALBANIA")
# html_2 = urllib.request.urlopen('https://al.usembassy.gov/updates_covid19/').read()
# pp.pprint(text_from_html(html_2))
#
# print("ARMENIA")
# html_2 = urllib.request.urlopen('https://am.usembassy.gov/u-s-citizen-services/covid-19-information/').read()
# pp.pprint(text_from_html(html_2))
