from math import log10
from elements import Term
import json
import sys

'''
the above is yang's library while I might not need to use yet.
'''

import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

class DocAnalyzer(object):
    """
    One DocAnalyzer per document.
    Input:
        filepath -- String document filepath
    """
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

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
        stats = {}
        for i, token in enumerate(tokens):
            if token in stats:
                term = stats[token]
                term.increment_tf()
                term.append_newPosition(i)
            else:
                stats[token] = Term(token, 1, i) # initialize Term() obj
        return stats


    def _beautify(self, filepath, **kwargs):
        '''
        **kwargs (default):
            title = True
            body = True
            anchor = True
            header = True
        '''
        if 'title' in kwargs and 'body' in kwargs and 'anchor' in kwargs and 'header' in kwargs:
            pass
        else:
            raise Exception('ERROR in _beautify(): missing kwargs.')

        f = open(filepath, 'r')
        raw = f.read()
        f.close()

        soup = BeautifulSoup(raw, 'html.parser')
        beauty = {'title': None, 'body': None, 'anchor': None, 'header': None}

        '''
        # soup.findAll() returns List<<bs4.beautiful.tag>>
        # <bs4.beautiful.tag>.text returns <unicode>
        '''

        if kwargs['title']:
            t = soup.findAll('title') # return empty list if there is no <title></>
            # if len(t) == 0:
            #     beauty['title'] = ""
            # else:
            beauty['title'] = ' '.join([tag.text.encode('ascii', 'ignore').lower() for tag in t])
        if kwargs['body']:
            b = soup.findAll('body')
            # if len(b) == 0:
            #     beauty['body'] = ""
            # elif len(t) > 1:
            #     raise Exception('Weird page found: more than one body is provided.')
            # else:
            #     beauty['body'] = b[0].text.encode('ascii', 'ignore').lower()
            beauty['body'] = ' '.join([tag.text.encode('ascii', 'ignore').lower() for tag in b])
        if kwargs['anchor']:
            anchors = soup.findAll('a', href = True)
            # the following code associates empty string with beauty['href'] when len(anchors) == 0
            url_text = {} # key_value pair, rather than text_url because text might be duplicated but url... not sure
            for a in anchors:
                url = a['href'].encode('ascii', 'ignore')
                ''' --------------------------------- '''
                # TODO: rel_url -> abs_url     # TODO
                ''' --------------------------------- '''
                text = a.text.encode('ascii', 'ignore').lower()
                if url in url_text:
                    ''' same url occurred more than once with different text '''
                    url_text[url] += text
                else:
                    url_text[url] = text
            '''
            beauty['anchor'] is a bit different than other 3 sections, its value is not <String> but {'url': 'text'}
            '''
            beauty['anchor'] = url_text
            '''
            anchor text is also part of the body text, merge them into 'body'
            '''
            beauty['body'] += ' '.join([url_text[k] for k in url_text])

        if kwargs['header']:
            h = []
            for i in range(1, 7):
                h.extend(soup.findAll('h{}'.format(i))) # a list of <h> tag object
            h = ' '.join([t.text.encode('ascii', 'ignore').lower() for t in h]) # join by \s
            beauty['header'] = h

        return beauty

    def analyze(self, filepath, title = True, body = True, anchor = True, header = True): # default setting for analyze()
        '''
        output:
            stats{ 'body': {token: Term() obj},
                   'title': {token: Term() obj},
                   'header': {token: Term() obj},
                   'anchor': {'url': 'anchor_text'},
                    }
        '''
        beauty = self._beautify(filepath, title = title, body = body, anchor = anchor, header = header)
        stats = {}
        for tag in beauty:
            if tag == 'anchor':
                stats[tag] = {}
                url_text = beauty[tag]
                for url, text in url_text.iteritems():
                    stats[tag][url] = self._tokenize(text)
                continue
            filtered = self._tokenize(beauty[tag])
            stats[tag] = self._terminize(filtered)
        return stats
