'''
This modules defines:
    Class:
        Term() - make each token separated by space or special characters a Term obj
        Document() - make each page a Document() obj, stores page-specific attributes that remain the same no matter what token it gets invertedly indexed to.
        InvDocument() - it is built on top of Document() and it has a few additional attributes pertaining to each page candidates in invert indexing process.
        MapCacher() - an abstract class for mapping and storage
        URL() - encapsulate url and its relevant information, such as outgoing links, anchor texts
    Functions:
            toAbsUrl() - This function defines how the program converts relative url to absolute url,
                         which is limited to the scope of this project.
'''



import math
from urlparse import urljoin



def toAbsUrl(root_url, rela_url):
    ''' The judgement call if the url is relative or absolute is very hard to make. Here one criteria is: if it contains 'ics.uci.edu' then it is absolute.
        Because the corpus is coming from that domain and its subdomains.
        Also note: the keys in bookkeeping file doesn't start with 'http://', but outgoing links might. '''
    if rela_url.startswith('http://'):
        abs_url = rela_url[7:].encode('ascii', 'ignore') # so if it actually points to some page in the corpus, we can find it.
    elif 'ics.uci.edu' in rela_url:
        abs_url = rela_url.encode('ascii', 'ignore')
    else:
        rela_url = rela_url.encode('ascii', 'ignore')
        abs_url = urljoin(root_url, rela_url)
    return abs_url


class Term(object):

    def __init__(self, token, tf, init_position):
        self.token = token
        self.tf = tf
        self.positions = [init_position]

    def increment_tf(self):
        self.tf += 1
        return ;

    def append_newPosition(self, i):
        self.positions.append(i)
        return ;


class Document(object):

    def __init__(self, idx, filepath, url, hubness = None, authority = None, pagerank = None):
        self.idx = idx
        self.filepath = filepath # abs path
        self.url = url # abs url
        self.params = {'hubness': None,
                        'authority': None,
                        'pagerank': None}

    def set(self, **kwargs):
        for k in kwargs:
            if not k in self.params:
                raise Exception('Error in Document() class: kwargs are limited as "hubness", "authority", "pagerank".')
            self.params[k] = kwargs[k]
        return ;

    def get(self, key):
        if not key in self.params:
            raise Exception('Error in Document() class: key is limited as one of the following: "hubness", "authority", "pagerank".')
        return self.params[key]


class InvDocument(Document):

    def __init__(self, idx, filepath, url, token, token_positions, token_tf):
        ''' Highlight.1: inheritance '''
        super(self.__class__, self).__init__(idx, filepath, url)
        self.token = token
        self.token_positions = token_positions
        self.token_tf = token_tf
        self.token_idf = None
        self.ranking_score = {}

    def set_idf(self, token_df, tot_docs):
        ''' Given token's document frequency and the number of total documents.
            This function computes the inverted document frequency. '''
        self.token_idf = math.log10(float(tot_docs) / token_df)
        return ;


class IdxItemMap(object):
    ''' This class implements an encapsulation of a dictionary data structure,
        dedicated to making the construction of certain type of mapping relations easy to manage.
        In the scope of this project:
            1. Dict<idx, Document>
            2. Dict<url, idx> '''
    def __init__(self):
        self._map = {}
        self._idx = 0

    def add(self, item, key = None):
        # if key is not specified, automatically index the item by the current self._idx
        if key is None:
            self._map[self._idx] = item
            self._idx += 1
        else:
            self._map[key] = item
        return ;

    def has(self, key):
        if key in self._map:
            return True
        else:
            return False

    def get_item_at(self, key):
        return self._map[key]

    def next_avai_idx(self):
        return self._idx

    def get_map(self):
        return self._map

    def iteritems(self):
        return self._map.iteritems()



class MapCacher(object):
    ''' This is a mapping relation manager class that allows users to create multiple dictionaries specified by key
    '''
    def __init__(self):
        self.docMap = {}

    def init_docMap(self, key = 'idx'):
        ''' after calling this function,
            if key == 'idx':
                a document mapping dictionary and initial doc index are created and associated with the given key within self.docMap
            elif key == 'url':
                a document mapping dictionary is created and associated with the given key within self.docMap '''
        self.docMap[key] = IdxItemMap()
        return ;

    def get_docMap(self, key = 'idx'):
        return self.docMap[key]





class URL():
    def __init__(self, url):
        self.url = url
        self.outgoing_links = set()
        self.anchorTokens = set()

    def add(self, anchorTokens = None, outgoing_links = None):
        if not anchorTokens is None:
            self.anchorTokens |= anchorTokens
        if not outgoing_links is None:
            self.outgoing_links |= outgoing_links
        return ;
