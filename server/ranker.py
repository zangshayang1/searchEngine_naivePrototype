import os
import pickle
import json
from docAnalyzer import DocAnalyzer
from nltk.tokenize import RegexpTokenizer



class Ranker(object):
    """
    In the front-end, one can call:
        from ranker import Ranker

        ranking<dict> = Ranker.retrieve_ranking(query<String>)
    """
    def __init__(self, invIdx_file, docIdx_file, corpus_dir, bookkeeping_file, pageRank_file):
        self.corpus_dir = corpus_dir
        self.docAnalyzer = DocAnalyzer(RegexpTokenizer(r'\w+'))

        with open(bookkeeping_file, 'r') as bkp:
            self.bkp = json.load(bkp)
        print 'bookkeeping loaded.'

        with open(pageRank_file, 'rb') as pr:
            self.pr = pickle.load(pr)
        print 'pageRank loaded.'

        with open(invIdx_file, 'rb') as iif:
            self.invIndex = pickle.load(iif)
        print 'invIndex loaded.'

        with open(docIdx_file, 'rb') as dif:
            self.docIndex = pickle.load(dif)
        print 'docIndex loaded.'


    ''' This function search over self.invIndex with token in tokens and return a list of InvDocument<> that contains all the tokens.
    Input:
        tokens List<String>
    Output:
        intersect: a list of invDocument.idx as List<int> intersected by query tokens throughout self.invIndex['body']
    '''
    def _intersect(self, tokens):
        tokens = set(tokens) # remove duplicates, query is always short
        tk_num = len(tokens)
        intersect = []
        doc_occurrence = {}
        for token in tokens:
            try:
                for invDoc in self.invIndex['body'][token]:
                    if invDoc.idx in doc_occurrence:
                        doc_occurrence[invDoc.idx] += 1
                    else:
                        doc_occurrence[invDoc.idx] = 1
            except KeyError():
                pass
        for idx, occurrence in doc_occurrence.iteritems():
            if occurrence == tk_num: # the invDocument<> is present in the list of every token in query
                intersect.append(idx)
        return intersect


    def _remove_duplicated(self, candidates):
        ''' under dev ... '''
        return candidates



    ''' This function ranks the incoming candidates, which is a List<InvDocument>, returns it.
    Input:
        candidates List<InvDocument>
    Output:
        sorted candidates List<(idx, score)>
    '''
    def _rank(self, candidates, qtks):
        for i in range(len(candidates)):
            ''' according to query, compute the score of the document indexed by idx. '''
            idx = candidates[i]
            candidates[i] = (idx, self._tfidf(idx, qtks) + 0.1 * self._pageRank(idx))
        return sorted(candidates, key = lambda x: x[1], reverse = True) # sort by the score of the document


    ''' This function computes the ranking score for the given invDocument<>
    Input:
        x int - invDocument.idx
        qtks List<String> - tokenized query
    Output:
        score float
    '''
    def _tfidf(self, x, qtks):
        score = 0
        for tk in qtks:
            ''' right now focus on the body only '''
            for invDoc in self.invIndex['body'][tk]:
                if x == invDoc.idx:
                    score += invDoc.token_tf * invDoc.token_idf
        return score


    def _pageRank(self, x):
        doc = self.docIndex.get_item_at(x)
        return self.pr[doc.url]


    ''' This function selects the top X candidates and retrieve document related information according to their index.
    Input: List<(Int, Float)>(invDocument.idx, score)
    Output: {'title': [doc1.title, doc2.title, ..., doc10.title],
             'url': [doc1.url, doc2.url, ..., doc10.url],
             'snippet': [doc1.snippet, doc2.snippet, doc3.snippet]
             }
    '''
    def _select(self, candidates, qtks, topX = 10):
        if len(candidates) < topX:
            pass
        else:
            candidates = candidates[:topX]

        top = {'title': [], 'url': [], 'snippet': []}

        for idx, _ in candidates:
            doc = self.docIndex.get_item_at(idx)
            title, snippet = self.docAnalyzer.snip(doc.filepath, qtks, cut = 200)
            top['title'].append(title)
            top['url'].append(doc.url)
            top['snippet'].append(snippet)
        return top


    ''' This function takes in query in a String format and search for the top10 results out of our ranking algorithm. '''
    def retrieve_ranking(self, q):

        ''' Output: dict<String, None> '''
        qtks = self.docAnalyzer.tokenize(q)

        ''' Output: List<Int>(invDocument.idx) '''
        candidates = self._intersect(qtks)

        ''' Output: List<Int>(invDocument.idx) '''
        candidates = self._remove_duplicated(candidates)

        ''' Output: List<(Int, Float)>(invDocument.idx, score) sorted according to their scores '''
        candidates = self._rank(candidates, qtks)

        ''' Output: Dict<k:v> refer to _select() for details '''
        top10 = self._select(candidates, qtks)

        return top10


if __name__ == '__main__':
    invIdx_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_invIndex.pkl'
    docIdx_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_docIndex.pkl'
    bookkeeping_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/bookkeeping.json'
    corpus_dir = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/test_WEBPAGES_RAW/'
    pageRank_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_pageRank.pkl'

    ranker = Ranker(invIdx_file, docIdx_file, corpus_dir, bookkeeping_file, pageRank_file)
    print ranker.retrieve_ranking("machine learning")
