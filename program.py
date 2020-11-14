import requests
from bs4 import BeautifulSoup
from lxml import html
from urllib.request import urlopen
import nltk
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import math

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

def DTermFrequencies(words, namafile): #words: array of string, namafile: string.txt
# return vektor yang koresponden dengan jumlah kemunculan kata pada dokumen berdasarkan kumpulan term pada words
    dtf = [0 for i in words]
    with open(namafile, 'r') as f:
        inWords = []
        for i in f:
            for j in word_tokenize(i):
                inWords.append(ps.stem(j))
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
    for i in word_tokenize(strInput):
        query.append(ps.stem(i))
    for i in range(len(qtf)):
        count = 0
        for j in query:
            if(j==words[i]):
                count += 1
        qtf[i] = count
    return qtf

def STokenWord(namafile): #namafile: string.txt
# return kata-kata yang unik dan udah distem dan tanpa stopwords
    words = []
    with open(namafile, 'r') as f:
        for i in f:
            kata = word_tokenize(i)
            for j in kata:
                if(not(ps.stem(j) in words) and not(j in stop_words)):
                    words.append(ps.stem(j))
    return words

def STokenWord_q(inputstr): #input query dari user
# return kata-kata yang unik dan udah distem dan tanpa stopwords dari query
    words_q = []
    kata = word_tokenize(inputstr)
    for j in kata:
        if(not(ps.stem(j) in words_q) and not(j in stop_words)):
            words_q.append(ps.stem(j))
    
    qtf = [0 for i in words_q]
    for i in range(len(qtf)):
        count = 0
        for j in kata:
            if(j==words_q[i]):
                count += 1
        qtf[i] = count
    return words_q, qtf

def lengthdoc (tf):
    square = 0
    for i in range (len(tf)):
        square += tf[i]**2
    length = math.sqrt(square)

    return length

def hasildot(qtf,DTermMatrix,R,C): #qtf, dtf: array of integer dari TF query dan dokumen
    Arrdot = []
    for i in range (1,R+1): #jumlah dokumen
        dotcount = 0
        for j in range (C):
            dotcount += qtf[j] * DTermMatrix[i][j]
        Arrdot.append(dotcount)

    return Arrdot

def fsentence (namafile):
    with open(namafile,'r') as file:
        first_line = file.readline()
    return first_line

#print(first_line)
def jumlahkata (namafile):
    with open(namafile,'r') as file: 
        count = 0     
        for line in file:        
            for word in line.split():          
                #print(word)
                count += 1 
    return count   

''' ++++++++ MAIN ++++++++ '''
#KAMUS
'''
words: array of string dari total term
query = array of array of integer untuk matriks TF(term frequency), 0..30 untuk query
a = array of array of integer untuk matriks TF(term frequency), 0..30 untuk dokumen
MatrixSim = array of integer untuk hasil cosine similarity per dokumen
           0..29 sesuai jumlah file
'''
titles = []
links = []
getDocuments(titles,links)
words_q = STokenWord_q("today a fine fine fine day")[0]
frequency_q = STokenWord_q("today a fine fine fine day")[1]
words = []
R = 30 

query = [[] for i in range(R)]
a = [[] for i in range(R)]
wordcount = []
first_sentence=[]

for i in range(30):
    namafile = 'document' + str(i+1) + '.txt'
    setOfWords = set(words)|set(STokenWord(namafile))
    words = list(setOfWords)
    first_sentence.append(fsentence(namafile))  
    wordcount.append(jumlahkata(namafile))
    
#print(words) #daftar term
#print(len(words)) #jumlah term

R = 30  #jumlah dokumen (D1 memiliki indeks 0, D2 memiliki indeks 1, dsb)
C = len(words) #jumlah term
query = QTermFrequencies(words, 'after')

for i in range(R):
    namafile = 'document' + str(i+1) + '.txt'
    a[i] = DTermFrequencies(words, namafile)   

DTermMatrix = [] #Matriks yang berisi frekuensi kemunculan term per dokumen
DTermMatrix.append(query)
for i in range(R):         
    b =[] 
    for j in range(C):    
        b.append(a[i][j]) 
    DTermMatrix.append(b) 

print("Matriks frekuensi kemunculan term dalam dokumen")
Mterm_0 = []
i=0
while (i < C):
    if DTermMatrix[0][i] != 0:
        Mterm_0.append(i)
    i += 1

#for i in range(R+1): 
    #for j in range (C):
        #if j in Mterm_0:
            #print(DTermMatrix[i][j], end = " ") 
    #print() 

#matriks transpose 
for j in range (C):
    for i in range(R+1):
        if j in Mterm_0:
            print(DTermMatrix[i][j], end = " ")
    print()

#simi
#for i in range(R+1):
    #for j in range (C):
        #print(DTermMatrix[i][j], end=" ")
    #print()

lengthQ = lengthdoc(query)

Arrsim = []
for i in range (R):
    namafile = 'document' + str(i+1) + '.txt'
    a[i] = DTermFrequencies(words, namafile)
    lengthD = lengthdoc(a[i])
    if lengthQ != 0:
        Arrsim.append((hasildot(query,DTermMatrix,R,C)[i])/(lengthQ*lengthD))
    else:
        Arrsim.append(2)
print(Arrsim)

#judul dokumen, jumlah kata, tingkat kemiripan, first_sentence
print("\nUrutan dokumen dengan nilai sim terurut mengecil")
arrTuple = [(Arrsim[i], wordcount[i], first_sentence[i], links[i], titles[i]) for i in range(len(Arrsim))]
def getKey(item): #diisi arrTuple
    return item[0]

print(sorted(arrTuple, key=getKey, reverse = True))