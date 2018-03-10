import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

INTERVAL = 5
MAX_FAIL = 100
BASE_URL = 'https://www.ted.com'
LIST_URL = BASE_URL + '/talks?page=%d'

def get_transcript(url, lang = None):
    if lang is not None:
        url = url + '?language=%s' % lang

    for i in range(MAX_FAIL):
        try:
            driver = webdriver.PhantomJS(driver_path)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            sentences = soup.select('div > div > div > section > div > div > p > span > a')
            langs = soup.select('div > div > div > section > div > div > select > option')    

            sentences = [s.text for s in sentences]
            langs = [l.get('value') for l in langs]

            driver.close()

            if len(sentences) > 0:
                break
            else:
                time.sleep(INTERVAL)
                print("retry... %d" % (i + 1))
        except:
            time.sleep(INTERVAL)
            print("error. retry... %d" % (i + 1))

    return sentences, langs

def write(dir_path, title, transcripts):
    for lang in transcripts.keys():
        sentences = transcripts[lang]

        if len(sentences) > 0:
            title = re.sub('\\?', '', title)
            title = re.sub('\\-', ' ', title)
            title = re.sub('\\s+', ' ', title)            
            fn = dir_path + '/' + '_'.join(title.split(' ')) + '-' + lang + '.txt'
            print(fn)
            f = codecs.open(fn, 'w', 'utf-8')

            f.write('\n'.join(sentences))

            f.close()

if __name__ == "__main__":
    driver_path = sys.argv[1]
    dir_path = './data'
    driver = webdriver.PhantomJS(driver_path)

    page_index = 1
    while True:
        driver.get(LIST_URL % page_index)
        time.sleep(INTERVAL)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        talk_list = soup.select('div > div > div > div > div > div > h4 > a')

        if len(talk_list) == 0:
            break

        for talk in talk_list:
            talk_url = BASE_URL + talk.get('href') + "/transcript"
            title = talk.text.strip()

            print(title)
            print(talk_url)

            transcripts = {}
            lang = 'en'
            while True:
                sentences, langs = get_transcript(talk_url, lang)
                print("%s %d" % (lang, len(sentences)))
                time.sleep(INTERVAL)
                
                transcripts[lang] = sentences

                lang = None
                for next_lang in langs:
                    if next_lang not in transcripts.keys():
                        lang = next_lang
                        break

                if lang is None:
                    break

            write(dir_path, title, transcripts)

        page_index += 1