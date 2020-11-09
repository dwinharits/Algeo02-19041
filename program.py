import requests
from bs4 import BeautifulSoup
from lxml import html
from urllib.request import urlopen
import csv
import nltk
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

def listToString(s):
    str = ""
    return(str.join(s))

def getText(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')

    text = []
    separator = '\n\n'
    for body in soup.find_all('div', class_='ArticleBody-articleBody'):
        for section in body.find_all('div', class_='group'):
            for paragraph in section.find_all('p'):
                text.append(paragraph.text)

    stringText = separator.join(text)
    return stringText

def getDocuments():
    source = requests.get("https://www.cnbc.com/world/?region=world").text

    soup = BeautifulSoup(source, 'lxml')

    i = 1
    for article in soup.find_all('div', class_='LatestNews-newsFeed'):
        title = (article.a.text)
        link = (article.a['href'])
        text = getText(link)

        file_name = 'document' + str(i) + '.txt'

        text_file = open(file_name, 'w')
        text_file.write(title)
        text_file.write('\n\n')
        text_file.write(text)
        text_file.close()
        i = i + 1

def stopwords(sentence):
    stop_words = set(stopwords.words('english'))

    word_tokens = word_tokenize(sentence)

    filtered_sentence = [w for w in word_tokens if not w in stop_words] 

    return listToString(filtered_sentence)

def stemming(sentence):
    ps = PorterStemmer()

    words = word_tokenize(sentence)

    stemmed = []
    for w in words:
        stemmed.append(ps.stem(w))
        stemmed.append(' ')

    return listToString(stemmed)