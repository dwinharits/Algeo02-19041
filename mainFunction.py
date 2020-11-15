import requests
from bs4 import BeautifulSoup
from lxml import html
from urllib.request import urlopen
import nltk
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import math
import re
import string
from flask import Flask, render_template, request

# KAMUS
'''
ps : buat stemming
stop_words : set stop words dari nltk
'''
ps = PorterStemmer()
stop_words = set(stopwords.words('english')) 

# KAMUS
'''
getText : prosedur buat link2 gitu gatau aqila yang buat
getDocuments : prosedur buat ngambil artikel dari web ke file txt
DTermFrequencies : fungsi yang ngereturn array of integer TF dari suatu dokumen
QTermFrequencies : fungsi yang ngereturn array of integer TF dari query
STokenWord : fungsi yang ngereturn array kata-kata yang unik elemennya dan gaada stopwords
sim : fungsi yang ngereturn cosine similarity(float)
'''

app = Flask(__name__)

query =""
titles = []
links = []
words = []
matriksTF = [[] for i in range(31)]
simIndex = [0 for i in range(30)]
wordcounts = [0 for i in range(30)]
firstlines = ['' for i in range(30)]
arrDict=[]

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/', methods=['POST','GET'])
def homepage_query():
    query = request.form['q']
    main(query)
    print(arrDict)
    return render_template('results.html', arrDict=arrDict)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/howtouse')
def howtouse():
    return render_template('howtouse.html')


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

def getDocuments(titles,links):
    source = requests.get("https://www.cnbc.com/world/?region=world").text

    soup = BeautifulSoup(source, 'lxml')

    i = 1
    for article in soup.find_all('div', class_='LatestNews-newsFeed'):
        title = (article.a.text)
        titles.append(title)
        link = (article.a['href'])
        links.append(link)
        text = getText(link)
        file_name = 'document' + str(i) + '.txt'

        text_file = open(file_name, 'w', encoding='utf-8', errors='ignore')
        text_file.write(text)
        text_file.close()
        i = i + 1

def clean(word):
    # fungsi ini mengembalikan word yang udah distem lebih rapih
    word = re.sub(r'[^\x00-x\x7F]+', '', word)
    word = re.sub(r'@\w+', '', word)
    word = word.lower()
    word = re.sub(r'[%s]' % re.escape(string.punctuation), '', word)
    word = re.sub(r'[0-9]', '', word)
    word = re.sub(r'\s{2,}', '', word)
    word = ps.stem(word)
    return word

def countTerm(arr, term):
    # mengembalikan banyaknya elemen arr yang sama dengan term
    count = 0
    for i in arr:
        if i==term:
            count += 1
    return count
    
def DTermFrequencies(words, namafile): #words: array of string, namafile: string.txt
    # return vektor yang koresponden dengan jumlah kemunculan kata pada dokumen berdasarkan kumpulan term pada words
    dtf = [0 for i in words]
    with open(namafile, 'r') as f:
        inWords = []
        for line in f:
            for word in line.split():
                inWords.append(clean(word))
        for i in range(len(words)):
            count = 0
            for j in inWords:
                if(j==words[i]):
                    count += 1
            dtf[i] = count
    return dtf

def QTermFrequencies(words, strInput): #words: array of strings, strInput: string   
    # return vektor yang koresponden dengan jumlah kemunculan kata pada query berdasarkan kumpulan term pada words
    qtf = [0 for i in words]
    query = []
    for word in strInput.split():
        query.append(clean(word))
    for i in range(len(qtf)):
        count = 0
        for word in query:
            if(word==words[i]):
                count += 1
        qtf[i] = count
    return qtf

def STokenWord(namafile): #namafile: string.txt
    # return kata-kata yang unik dan udah distem dan tanpa stopwords
    words = []
    with open(namafile, 'r') as f:
        for line in f:
            for word in line.split():
                if(clean(word) not in words) and (word not in stop_words):
                    words.append(clean(word))
    if('' in words):
        words.remove('')
    if(' ' in words):
        words.remove(' ')
    return words

def WordTokenize(namafile):
    # fungsi ini mengembalikan array of word dari dokumen dengan nama namafile
    words = []
    with open(namafile, 'r') as f:
        for line in f:
            for word in line.split():
                if(word!='' and word!=' '):
                    words.append(clean(word))
    return words

def getFirstSentence(namafile):
    # fungsi ini mengembalikan kalimat pertama pada text file yang telah dikondisikan getDocuments()

    # KAMUS LOKAL #
    '''
    line = kalimat(string)
    '''

    # ALGORITMA #
    with open(namafile, 'r') as f:
        line = f.readline()
        return line

def getJumlahKata(namafile):
    # fungsi getJumlah kata mengembalikan jumlah kata dalam text file

    # KAMUS LOKAL #
    '''
    count: integer
    line: kalimat(string)
    word: kata(string)
    '''

    # ALGORITMA #
    with open(namafile,'r') as file: 
        count = 0     
        for line in file:        
            for word in line.split():          
                word = clean(word)
                if(word!='' and word!=' '):
                    count+=1
    return count

def sim(qtf,dtf):
    # qtf, dtf: array of integer dari TF query dan dokumen
    # fungsi sim mengembalikan nilai cosine similarity antara query dan dokumen
    # jika dtf atau qtf berelemen 0 seluruhnya maka sim menghasilkan 0

    # KAMUS LOKAL #
    '''
    dotcount, squareQ, squareD, lengthQ, lengthD: float
    '''

    # ALGORITMA #
    dotcount = 0
    squareQ = 0
    squareD = 0

    for i in range (len(dtf)):
        dotcount += qtf[i] * dtf[i]
        squareQ += qtf[i]**2
        squareD += dtf[i]**2

    lengthQ = math.sqrt(squareQ)
    lengthD = math.sqrt(squareD)

    if(lengthQ*lengthD == 0):
        return 0
    else:
        return dotcount/(lengthQ*lengthD)

def getKey(item):
    # getKey menerima array dan mengembalikan elemen pertamanya
    # digunakan pada proses sorting di main
    return item[0]

def uniqueList(listI):
    # mengembalikan list yang unik berdasarkan listI(tidak ada elemen listI yang mengulang)

    # KAMUS LOKAL #
    '''
    listB: list
    '''

    # ALGORTIMA #
    listB = []
    for element in listI:
        if element not in listB:
            listB.append(element)
    return listB
    

####################MAIN#########################

def main(query):
    
    # prosedur main menghasilkan term table berdasarkan query dan sorted tuple berdasarkan nilai
    #   cosine similarity antara dokumen-dokumen dengan query

    # KAMUS LOKAL #
    '''
    titles: array of string, 0..29 untuk menyimpan judul
    links: array of string, 0..29 untuk menyimpan link dokumen terkait
    words: array of string, dinamis, sebagai koleksi word yang telah distem dan unik dari seluruh dokumen
    matriksTF: array of array of int, 0..30 sebagai matriks vektor term frequencies
    simIndex: array of real, 0..29 yang menyimpan nilai cosine similarity tiap dokumen
    wordcounts: array of integer, 0..29 menyimpan jumlah kata tiap-tiap dokumen
    firstlines: array of string, 0..29 menyimpan kalimat pertama tiap-tiap dokumen
    tQuery: array of string, menyimpan query dalam bentuk array of string
    '''

    # ALGORITMA #
    titles = []
    links = []
    getDocuments(titles,links)

    words = []
    matriksTF = [[] for i in range(31)]
    simIndex = [0 for i in range(30)]
    wordcounts = [0 for i in range(30)]
    firstlines = ['' for i in range(30)]

    # ngebuat library term dari seluruh dokumen
    for i in range(1,31):
        namafile = 'document' + str(i) + '.txt'
        setOfWords = set(words)|set(STokenWord(namafile))
        words = list(setOfWords)

    #ngeset matriksTF
    matriksTF[0] = QTermFrequencies(words, query)

    for i in range(1,31):
        namafile = 'document' + str(i) + '.txt'
        matriksTF[i]= DTermFrequencies(words, namafile)

    # ngeset array jumlah kata
    for i in range(30): 
        namafile = 'document' + str(i+1) + '.txt'
        wordcounts[i] = getJumlahKata(namafile)

    # ngeset array jumlah firstlines
    for i in range(30):
        namafile = 'document' + str(i+1) + '.txt'
        firstlines[i] = getFirstSentence(namafile)

    # ngeset array jumlah simIndex
    for i in range(1,31):
        simIndex[i-1] = sim(matriksTF[0], matriksTF[i])

    # nanti ke-print simIndexnya, tinggal disort buat tau yang
    # mana dokumen paling relevan, jangan lupa indeksnya 0..29
    global arrDict
    arrDict = [
        {
            'sim':0,
            'title': '',
            'link': '',
            'firstline': '',
            'wordcount': 0
        } for i in range(30)]

    for i in range(30):
        arrDict[i]['sim'] = simIndex[i] 
        arrDict[i]['title'] = titles[i]
        arrDict[i]['link'] = links[i]
        arrDict[i]['firstline'] = firstlines[i]
        arrDict[i]['wordcount'] = wordcounts[i]

    arrDict = sorted(arrDict, key = lambda i: i['sim'], reverse = True)

    # buat term table
    tQuery = uniqueList(query.split())
    
    for term in tQuery:
        print(term, end=': ')
        for i in range(30):
            namafile = 'document' + str(i+1) + '.txt'
            print(countTerm(WordTokenize(namafile),term), end=' ')
        print('')

if __name__ == '__main__':
    app.run(debug=True)








