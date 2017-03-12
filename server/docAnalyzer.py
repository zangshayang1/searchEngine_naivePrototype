import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from bs4 import BeautifulSoup

from elements import Term
import re
from urlparse import urljoin



class DocAnalyzer(object):
    """
    One DocAnalyzer per document.
    Input:
        filepath -- String document filepath
    """
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.stemmer = PorterStemmer()

    def tokenize(self, data):
        tokens_position = {}
        tokens = self._tokenize(data)
        stemmed = [self.stemmer.stem(token) for token in tokens]
        filtered = filter(lambda x : x not in stopwords.words('english'), stemmed)
        return filtered

    ''' The following implements a very robust tokenization function. '''
    def _tokenize(self, data):
        """
        @ input: String
        @ outputs: List<token>
        """

        def is_alphaNumeric(char):
            """
            @ input: char
            @ return: bool if char is alphaNumeric or not
            """
            if 48 <= ord(char) <= 57 or 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122:
                return True
            else:
                return False

        token_stream = []
        i = 0
        l = len(data)
        while i < l:
            while i < l and not is_alphaNumeric(data[i]):
                i += 1
            start = i
            # now start ptr to the first occurrence of alphaNumeric
            while i < l and is_alphaNumeric(data[i]):
                i += 1
            end = i
            # now end ptr to the first occurence of non-alphaNumeric after start
            tk = data[start : end].lower()
            if tk != "":
                token_stream.append(tk)
        return token_stream

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


    def _beautify(self, **kwargs):
        '''
        Input:
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

        f = open(self.filepath, 'r')
        raw = f.read()
        f.close()

        soup = BeautifulSoup(raw, 'html.parser')
        beauty = {'title': None, 'body': None, 'anchor': None, 'header': None}

        '''
        # soup.findAll() returns List<<bs4.beautiful.tag>>
        # <bs4.beautiful.tag>.text returns <unicode>
        '''

        if kwargs['body']:
            b = soup.findAll('body')
            ''' body.text includes anchor text and header text in body '''
            beauty['body'] = ' '.join([tag.text.encode('ascii', 'ignore').lower() for tag in b])
        else:
            raise Exception("Error in _beautify(): 'body' must be specified as True.")

        if kwargs['title']:
            t = soup.findAll('title') # return empty list if there is no <title></>
            beauty['title'] = ' '.join([tag.text.encode('ascii', 'ignore').lower() for tag in t])

        if kwargs['anchor']:
            anchors = soup.findAll('a', href = True)
            beauty['anchor'] = self._extract_anchorInfo_from(anchors)
            ''' beauty['anchor'] is a bit different than other 3 sections, its value is not <String> but {'url': 'text'} going to output with only tokenize() '''

        if kwargs['header']:
            beauty['header'] = self._extract_headerInfo_from(soup, levels = [1, 2, 3])

        return beauty


    ''' This function is callable within _beautify(), extracting header text specified by given levels.
    Input:
        soup from BeautifulSoup
        levels List<Int> specifying levels of headers that are to be extracted.
    Output:
        h String
    '''
    def _extract_headerInfo_from(self, soup, levels = [1, 2, 3]): # h1 - h3 will be appropriate size for important header info
        h = []
        for i in levels:
            h.extend(soup.findAll('h{}'.format(i)))
        h = ' '.join([t.text.encode('ascii', 'ignore').lower() for t in h]) # join by space
        return h


    ''' This function is callable within _beautify(), extracting url, anchor text from the soup.
        This function is not elegant enough due to it is depending on <BeautifulSoup.anchor.tag> obj.

    Input: List<BeautifulSoup.anchor.tag>(anchors)
    Output: Dict<String : String>(url : anchor text)
    '''
    def _extract_anchorInfo_from(self, anchors):
        url_text = {}
        for a in anchors:
            url = a['href'].encode('ascii', 'ignore')
            if 'ics.uci.edu' not in url:
                url = urljoin(self.url, url) # convert relative url to absolute form

            text = a.text.encode('ascii', 'ignore').lower()
            if url in url_text:
                url_text[url] += text # same url occurred more than once with different text
            else:
                url_text[url] = text
        return url_text


    def analyze(self, filepath, url, title = True, body = True, anchor = True, header = True): # default setting for analyze()
        '''
        Input:
            filepath : String : the absolute filepath of the document passed in this function
            url : String : the absolute url of the document passed in this function
        output:
            stats{ 'body': {token: Term() obj},
                   'title': {token: Term() obj},
                   'header': {token: Term() obj},
                   'anchor': {'url': 'anchor_text'},
                    }
        '''
        # why do we need url? we need the absolute url to convert relative urls found in the anchors to their absolute format.
        self.url = url
        self.filepath = filepath
        beauty = self._beautify(title = title, body = body, anchor = anchor, header = header)
        stats = {}
        for tag in beauty:
            if tag == 'anchor':
                stats[tag] = {}
                url_text = beauty[tag]
                for url, text in url_text.iteritems():
                    stats[tag][url] = self.tokenize(text)
                continue
            filtered = self.tokenize(beauty[tag])
            stats[tag] = self._terminize(filtered)
        return stats


    ''' This function returns a snapshot of the page at the given filepath, which includes title and a snippet of body that's related to query tokens.
    Input:
        filepath String
        qtks List<String> : query tokens
        cut Int : the limit of words in the returned snippet
    Output:
        title String
        body snippet String
    '''
    def snip(self, filepath, qtks, cut = 200):
        with open(filepath, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        title, snippet = None, []

        if soup.title:
            title = soup.title.get_text().encode('ascii', 'ignore').rstrip()
        '''
        h1 - h3 would be appropriate size for header to be shown in the page snippet.
        you should choose the one that's closest to the query if title is not available.
        '''
        # else:
        #     for i in range(1, 4):
        #         h = soup.find('h{}'.format(i))

        ''' clean body a little bit '''
        if soup.body:
            body = soup.body.get_text().encode('ascii', 'ignore')
        else:
            body = soup.get_text()

        body = re.sub(r'\n\s*\n', '\n', body) # substityde multiple '\n' with single '\n'

        for tk in qtks:
            length = len(tk)
            for i in range(len(body)):
                if body[i:i+length] == tk:
                    j = i
                    while j >= 0 and body[j] != '.' and body[j] != '\n':
                        j -= 1
                    k = i + length
                    while k < len(body) and body[k] != '.' and body[k] != '\n':
                        k += 1
                    snippet.append(body[j+1: k-1])
        if len(snippet) == 0:
            print 'INFO: snip(): nothing extracted from {}.'.format(filepath)
            return title, snippet

        snippet = ' '.join(snippet)
        return title, snippet[:cut]
