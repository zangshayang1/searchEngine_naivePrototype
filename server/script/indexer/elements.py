'''
This module defines the element classes used in SearchEngine project
'''

import pickle
import math

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
    def __init__(self, idx, filepath, url):
        self.idx = idx
        self.filepath = filepath
        self.url = url

class InvDocument(Document):
        ''' in inverted indexing table: each doc also has the following attrs so info about the indexing term can be easily stored/accessed.
            these are set during _invert() process when each Document() obj meets Term() obj.
        '''
    def __init__(self, idx, filepath, url, token, token_positions, token_tf):
        ''' this is the best part No.1 of this project:
        initialize what is defined in InvDocument's super class for the current class InvDocument. '''
        super(self.__class__, self).__init__(idx, filepath, url)
        self.token = token
        self.token_positions = token_positions
        self.token_tf = token_tf
        self.token_idf = None

    def set_idf(self, token_df, tot_docs):
        '''
        Given token's document frequency and the number of total documents.
        This function computes the inverted document frequency.
        '''
        self.token_idf = math.log10(float(tot_docs) / token_df)
        return ;






class IdxItemMap(object):
    """
    this is to facilitate indexing document process {idx: Document}
    """
    def __init__(self, start_idx = 0):
        self._map = {}
        self._idx = start_idx

    def add(self, item, idx):
        self._map[idx] = item
        return ;

    def get_item_at(self, idx):
        return self._map[idx]

    def next_avai_idx(self):
        idx = self._idx
        self._idx += 1
        return idx


# class tknItemMap(object):
#     """
#     this is to facilitate mapping token process {token: Term}
#     """
#     def __init__(self):
#         self._map = {}
#
#     def add_new(self, token, item):
#         self._map[token] = item
#         return ;
#
#     def has(self, token):
#         return token in self._map
#
#     def remove(self, token):
#         print "Under dev..."
#         pass
#
#     def get_map(self):
#         return self._map


class MapCacher(object):
    def __init__(self):
        self.docMap = {}

    def init_docMap(self, name = 'main', doc_start_idx = 0):
        '''
        after calling this function, a document mapping dictionary and initial doc index are created and associated with the given name within self.docMap
        '''
        self.docMap[name] = IdxItemMap(doc_start_idx)
        return ;

    def get_docMap(self, name = 'main'):
        return self.docMap[name]

    def load(self, filepath, mode = 'pickle'):
        if mode == 'pickle':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        elif mode == 'json':
            raise Exception('Under dev...')
        else:
            raise Exception('Error: "mode" can be either "pickle" or "json".')

    def save(self, filepath, mode = 'pickle'):
        if mode == 'pickle':
            with open(filepath, 'wb') as f:
                pickle.dump(self.docMap, f)
                return ;
        elif mode == 'json':
            raise Exception('Under dev...')
        else:
            raise Exception('Error: "mode" can be either "pickle" or "json".')
