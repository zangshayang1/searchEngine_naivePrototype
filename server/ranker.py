import os
import pickle
import json
import math
import time
from docAnalyzer import DocAnalyzer
from nltk.tokenize import RegexpTokenizer
import config



class Ranker(object):
    ''' Interface

            In the front-end, one can call:
                from ranker import Ranker
                ranking<dict> = Ranker.retrieve_ranking(query<String>) '''

    def __init__(self, corpus_dir, bkp_file, invIndex_file, pageMap_file):
        print 'Initializing ... {}'.format(time.time())
        if corpus_dir is None or bkp_file is None or invIndex_file is None or pageMap_file is None:
            raise Exception('Error in Ranker() : Missing arguments.')

        self.corpus_dir = corpus_dir

        self.bkp = self._load(bkp_file, mode = 'json')

        self.pageMap = self._load(pageMap_file, mode = 'pkl')
        self.mainDocMap = self.pageMap.get_docMap(key = 'idx')
        self.urlDocMap = self.pageMap.get_docMap(key = 'url')

        self.invIndex = self._load(invIndex_file, mode = 'pkl')

        self.docAnalyzer = DocAnalyzer(RegexpTokenizer(r'\w+'))

    ''' This function search over self.invIndex with query tokens and return a list of numbers pointing at those documents that contains all the tokens.
            Input:
                tokens List<String>
            Output:
                intersect: a list of invDocument.idx as List<int> intersected by query tokens throughout self.invIndex['body'] '''
    def _intersect(self, qtks):
        qtks = set(qtks) # remove duplicates, query is always short
        tk_num = len(qtks)
        intersect = []
        doc_occurrence = {}
        for tk in qtks:
            try:
                for invDoc in self.invIndex['body'][tk]:
                    if invDoc.idx in doc_occurrence:
                        doc_occurrence[invDoc.idx] += 1
                    else:
                        doc_occurrence[invDoc.idx] = 1
            except KeyError():
                pass
        for idx in doc_occurrence:
            if doc_occurrence[idx] == tk_num: # the invDocument<> is present in the list of every token in query
                intersect.append(idx)
        return intersect


    ''' This function ranks the incoming candidates, which is a List<InvDocument.idx>
            Input:
                candidates List<InvDocument.idx>
            Output:
                sorted candidates List<(idx, score)> '''
    def _rank(self, candidates, qtks):
        for i in range(len(candidates)):
            ''' according to query, compute the score of the document indexed by idx. '''
            idx = candidates[i]
            candidates[i] = (idx, self._tfidf(idx, qtks) +
                                  math.log(self._authority(idx) + 1) +
                                  math.log(self._hubness(idx) + 1) +
                                  2 * self._pageRank(idx) +
                                  0.6 * self._urlHits(idx, qtks) +
                                  1.1 * self._titleHits(idx, qtks) +
                                  2 * self._anchorHits(idx, qtks)
                                  )
        return sorted(candidates, key = lambda x: x[1], reverse = True) # sort by the score of the document


    ''' This function computes the tf-idf score for the given invDocument<>
            Input:
                x int - invDocument.idx
                qtks List<String> - tokenized query
            Output:
                score float '''
    def _tfidf(self, x, qtks):
        score = 0
        for tk in qtks:
            for invDoc in self.invIndex['body'][tk]:
                if x == invDoc.idx:
                    score += invDoc.token_tf * invDoc.token_idf
        return score

    ''' This function computes the score gained because the document's title includes query tokens
            Input and Output same as _tfid() '''
    def _titleHits(self, x, qtks):
        score = 0
        for tk in qtks:
            for invDoc in self.invIndex['title'][tk]:
                if x == invDoc.idx:
                    score += 10 # 10pts for each token match found in title
        return score

    ''' This function computes the score gained because the document's url includes query tokens
            Input and Output same as _tfid() '''
    def _urlHits(self, x, qtks):
        score = 0
        doc = self.mainDocMap.get_item_at(x)
        utks = self.docAnalyzer.tokenize(doc.url)
        for qtk in qtks:
            for utk in utks:
                if qtk == utk:
                    score += 10 # 10pts for each token match found in url
        return score

    ''' This function computes the score gained because the there are some anchor tokens found in the query tokens pointing to the current document
            Input and Output same as _tfid() '''
    def _anchorHits(self, x, qtks):
        score = 0
        for tk in qtks:
            for docIdx in self.invIndex['anchor'][tk]:
                if x == docIdx:
                    score += 10
        return score

    ''' This function returns the authority of the current document indexed by x
            Input:
                x - Int document index
            Output:
                authority score '''
    def _authority(self, x):
        doc = self.mainDocMap.get_item_at(x)
        return doc.get('authority')

    ''' This function returns the hubness of the current document indexed by x
            Input and Output same as _authority() '''
    def _hubness(self, x):
        doc = self.mainDocMap.get_item_at(x)
        return doc.get('hubness')

    ''' This function returns the pagerank of the current document indexed by x
            Input and Output same as _authority() '''
    def _pageRank(self, x):
        doc = self.mainDocMap.get_item_at(x)
        return doc.get('pagerank')

    ''' This function selects the top X candidates and retrieve document related information according to their index.
            Input: List<invDocument.idx, score)>
            Output: {'title': [doc1.title, doc2.title, ..., doc10.title],
                     'url': [doc1.url, doc2.url, ..., doc10.url],
                     'snippet': [doc1.snippet, doc2.snippet, doc3.snippet]
                    } '''
    def _select(self, candidates, qtks, topX = 10):
        if len(candidates) < topX:
            pass
        else:
            candidates = candidates[:topX]

        top = {'title': [], 'url': [], 'snippet': []}

        for idx, _ in candidates:
            doc = self.mainDocMap.get_item_at(idx)
            title, snippet = self.docAnalyzer.snip(doc.filepath, qtks, cut = 200)
            top['title'].append(title)
            top['url'].append(doc.url)
            top['snippet'].append(snippet)
        return top


    ''' This function takes in query in a String format and search for the top10 results out of our ranking algorithm. '''
    def retrieve_ranking(self, q):

        ''' Tokenize the query
                Input: query - String
                Output: qtks - List<String>, query tokens '''
        qtks = self.docAnalyzer.tokenize(q)

        # NOTE: This selection should be expanded to take anchor text into consideration. However it involves the following difficulties:
        #       If the anchor text "Big Blue" points to page A about "IBM" and page B about "Big Blue Bus",
        #           how would you score these two pages and all the other pages that contain "Big Blue" in body text?
        #       Clearly, IBM will not use "Big Blue" on their own webpages so we won't find a good "tfidf" measure of it according to the query.
        candidates = self._intersect(qtks)

        candidates = self._rank(candidates, qtks)

        top10 = self._select(candidates, qtks)

        return top10

    ''' The exact same _load() function as in indexer.py. Code reusability needs to be improved. But I am just being lazy here. '''
    def _load(self, filepath, mode = 'json'):
		if not os.path.exists(filepath):
			raise Exception("MissingFile: {} doens't exist.".format(filepath))

		if mode == 'json':
			with open(filepath, 'r') as handler:
				return json.load(handler)
		elif mode == 'pkl':
			with open(filepath, 'rb') as handler:
				return pickle.load(handler)
		else:
			raise Exception("Error in Indexer: other mode under dev...")


if __name__ == '__main__':
    bkp_file = config.BOOKKEEPING_FILE
    corpus_dir = config.WORKING_DIR

    invIndex_file = config.INVINDEX_FILE
    pageMap_file = config.PAGEMAP_FILE

    ranker = Ranker(corpus_dir, bkp_file, invIndex_file, pageMap_file)

    print ranker.retrieve_ranking("machine learning")
