'''
This module defines the element classes used in SearchEngine project
'''

import pickle

class Term(object):
    def __init__(self, term, tf, init_position):
        self.term = term
        self.tf = tf
        self.positions = [init_position]

        self.idf = None # later computed

    def increment_tf(self):
        self.tf += 1
        return ;

    def append_newPosition(self, i):
        self.positions.append(i)
        return ;

class Document(object):
    def __init__(self, idx, filepath, url):
        self.idx = idx
        self.filepath = filepath
        self.url = url
        self.tf = None






class IdxItemMap(object):
    """
    this is to facilitate indexing document process {idx: Document}
    """
    def __init__(self, start_count = 0):
        self._map = {}
        self._nextCount = start_count

    def add_new(self, item):
        self._map[self._nextCount] = item
        self._nextCount += 1
        return ;

    def get_map(self):
        return self._map

    def get_next_count(self):
        return self._nextCount

class tknItemMap(object):
    """
    this is to facilitate mapping token process {token: Term}
    """
    def __init__(self):
        self._map = {}

    def add_new(self, token, item):
        self._map[token] = item
        return ;

    def has(self, token):
        return token in self._map

    def remove(self, token):
        print "Under dev..."
        pass

    def get_map(self):
        return self._map


class MapCacher(object):
    def __init__(self):
        self.docMap = {}
        self.termMap = {}

    def init_docMap(self, name, doc_start_idx = 0):
        '''
        after calling this function, a document mapping dictionary and initial doc index are created and associated with the given name within self.docMap
        '''
        self.docMap[name] = IdxItemMap(doc_start_idx)
        return ;

    def init_termMap(self, name):
        self.termMap[name] = tknItemMap()
        return ;

    def load(self, filepath, mode = 'pickle'):
        if mode == 'pickle':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        elif mode == 'json':
            raise Exception('Under dev...')
        else:
            raise Exception('Error: "mode" can be either "pickle" or "json".')

    def store(self, mapdict, filepath, mode = 'pickle'):
        if mode == 'pickle':
            with open(filepath, 'wb') as f:
                pickle.dump(mapdict, f)
                return ;
        elif mode == 'json':
            raise Exception('Under dev...')
        else:
            raise Exception('Error: "mode" can be either "pickle" or "json".')
