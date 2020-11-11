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

def getDocuments():
    source = requests.get("https://www.cnbc.com/world/?region=world").text

    soup = BeautifulSoup(source, 'lxml')

    i = 1
    for article in soup.find_all('div', class_='LatestNews-newsFeed'):
        title = (article.a.text)
        link = (article.a['href'])
        text = getText(link)

        file_name = 'document' + str(i) + '.txt'

        text_file = open(file_name, 'w', encoding='utf-8', errors='ignore')
        text_file.write(title)
        text_file.write('\n\n')
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

def simi(qtf,DTermMatrix,R,C): #qtf, dtf: array of integer dari TF query dan dokumen

    squareQ = 0
    for i in range (len(qtf)):
        squareQ += qtf[i]**2
    lengthQ = math.sqrt(squareQ)

    Arrsim = []
    for i in range (R): #jumlah dokumen
        dotcount = 0
        squareD = 0
        for j in range (C):
            dotcount += qtf[j] * DTermMatrix[i][j]
            squareD += DTermMatrix[i][j]**2
        lengthD = math.sqrt(squareD)
        Arrsim.append(dotcount/(lengthD*lengthQ))

    return Arrsim

''' ++++++++ MAIN ++++++++ '''
#KAMUS
'''
words: array of string dari total term
query = array of array of integer untuk matriks TF(term frequency), 0..30 untuk query
a = array of array of integer untuk matriks TF(term frequency), 0..30 untuk dokumen
simIndex = array of integer untuk hasil cosine similarity per dokumen
           0..29 sesuai jumlah file
'''
#getDocuments()

words = []
query = [[] for i in range(30)]
a = [[] for i in range(30)]
simIndex = [0 for i in range(30)]

for i in range(30):
    namafile = 'document' + str(i+1) + '.txt'
    setOfWords = set(words)|set(STokenWord(namafile))
    words = list(setOfWords)
    
print(words) #daftar term
print(len(words)) #jumlah term

R = 30  #jumlah dokumen (D1 memiliki indeks 0, D2 memiliki indeks 1, dsb)
C = len(words) #jumlah term

query = QTermFrequencies(words, 'after')
#print(query)

for i in range(R):
    namafile = 'document' + str(i+1) + '.txt'
    a[i] = DTermFrequencies(words, namafile)   
    #print(a[i])

DTermMatrix = [] #Matriks yang berisi frekuensi kemunculan term per dokumen
for i in range(R):         
    b =[] 
    for j in range(C):    
        b.append(a[i][j]) 
    DTermMatrix.append(b) 
 
# Mencetak DTermMatriks
print("Matriks frekuensi kemunculan term dalam dokumen")
for i in range(R): 
    for j in range(C): 
        print(DTermMatrix[i][j], end = " ") 
    print() 

# Membentuk matriks dengan key : nilai sim; value : indeks
MatrixSim = simi(query,DTermMatrix,R,C)

d =[]
for i in range (R):
    d.append(i)

Mindeks_sim = dict(zip(d, MatrixSim))
#print(Mindeks_sim)

# Mengurutkan dictionary berdasarkan value (nilai sim)
sort = {k: v for k, v in sorted(Mindeks_sim.items(), key=lambda item: item[1], reverse=True)}
print("\nUrutan dokumen dengan nilai sim terurut mengecil")
print(sort)

    

