from math import log10
import json


import nltk
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

class DocAnalyzer(object):
    """
    One DocAnalyzer per document.
    Input:
        filepath -- String document filepath
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.stats = {}

    def _tokenize(self, data):
        '''
        Input:
            data -- String
        '''
        tokens = self.tokenizer.tokenize(data)
        filtered = filter(lambda token: token not in stopwords.words('english'), tokens)
        return filtered

    def _terminize(self, tokens):
        '''
        Input:
            tokens -- List<String>
        '''
        for i, token in enumerate(tokens):
            if token in self.stats:
                term = self.stats[token]
                term.increment_tf()
                term.append_newPosition(i)
            else:
                self.stats[token] = Term(token, 1, i) # initialize Term() obj


    def beautify(self, title = True, body = True, anchor = True, header = True):
        beauty = []
        f = open(self.filepath, 'r')
        raw = f.read()
        f.close()

        soup = BeautifulSoup(raw, 'html.parser')

        '''
        e.g. beauty {'body' : []}

        # soup.findAll() returns List<<bs4.beautiful.tag>>
        # <bs4.beautiful.tag>.text returns <unicode>
        '''
        if title:
            t = soup.findAll('title') # return empty list if there is no <title></>
            if len(t) == 0:
                beauty['title'] = ""
            elif len(t) > 1:
                raise Exception('Weird page found: more than one title is provided.')
            else:
                beauty['title'] = t[0].text.encode('ascii', 'ignore').lower()
        if body:
            b = soup.findAll('body')
            if len(b) == 0:
                beauty['body'] = ""
            elif len(t) > 1:
                raise Exception('Weird page found: more than one body is provided.')
            else:
                beauty['body'] = b[0].text.encode('ascii', 'ignore').lower()
        if anchor:
            anchors = soup.findAll('a', href = True)
            for a in anchors:
                url = a['href'].encode('ascii', 'ignore')
                anchor_text = a.text.encode('ascii', 'ignore').lower()
                beauty['href'] =

            h = []
            for i in range(1, 7):
                h.extend(soup.findAll('h{}'.format(i)))

            beauty['']


import sys

"""
how to use nltk
"""
# from nltk.tokenize import RegexpTokenizer
# data = "haha, hehe    heanfhjkKL HF KJSF HFKLH FL    EH O3IH haha hehe"
# tokenizer = RegexpTokenizer(r'\w+')
# tokens = tokenizer.tokenize(data)
# print tokens

# from nltk.corpus import stopwords
# nltk.download()
# print stopwords.words('english')

"""
how to use bs4

soup.find() returns BeautifulSoup.tag, which you can call tag.text() or tag['href'] ...
soup.findAll() returns a list of such tags
"""

# with open(sys.argv[1], 'r') as f:
#     raw = f.read()
#     soup = BeautifulSoup(raw, 'html.parser')

#     print soup.body
#
#     print '-------- title --------'
#     print soup.findAll('title')
    #
    # print '-------- body ---------'
    # print soup.find('body')
    #
    # print '-------- body ---------'
    # print type(soup.find('body'))
    #
    # print '-------- body text ---------'
    # print soup.find('body').text.encode('ascii', 'ignore').lower()
    #
    # for anchor in soup.findAll('a', href = True):
    #     print anchor['href']
    #     print anchor.text
    # if soup.title and soup.title.string:
    #     title = soup.title.string.encode('ascii', 'ignore').lower()
    # else:
    #     title = ""
    # data = soup.get_text().lower().encode('ascii', 'ignore')
    # print title
    # print data
    #
    # if soup.title:
    #     if soup.title.string is not None:
    #         title = soup.title.string.encode('ascii', 'ignore').lower()
    # else:
    #     title = ""
    # data = soup.get_text().lower().encode('ascii', 'ignore')
    # return title, data




class DocAnalyzer():
    """This class takes HTML file and return tokens"""
    def __init__(self):
        self.title

    def extractData(self, path):
        global title
        raw = open(path, 'r').read()
        soup = BeautifulSoup(raw, 'lxml')
        if soup.title:
            if soup.title.string is not None:
                title = soup.title.string.encode('ascii', 'ignore').lower()
        else:
            title = ""
        data = soup.get_text().lower().encode('ascii', 'ignore')
        return title, data

    def tokenize(self, data):
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(data)
        filtered_tokens = tokens
        for token in tokens: #remove stop words
            if token in stopwords.words('english'):
                filtered_tokens.remove(token)
        return filtered_tokens

    def token_with_position(self, tokens):
        token_position = {}
        pos = 0
        for token in tokens:
            if token in token_position:
                token_position[token].append(pos)
            else:
                token_position[token] = [pos]
            pos += 1
        return token_position

    def frequency(self, token_position):
        freq = {}
        for token, postions in token_position.items():
            freq[token] = len(postions)
        return freq

    def tf(self, frequency):
        tf = {}
        for token, freq in frequency.items():
            term_freq = 1 + log10(freq)
            tf[token] = term_freq
        return tf

    def idf(self, df):
        N = 37000.0
        idf = log10(N / df)
        return idf
