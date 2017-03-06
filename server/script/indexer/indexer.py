from docAnalyzer import DocAnalyzer
from nltk.tokenize import RegexpTokenizer
from elements import Document, MapCacher, InvDocument
import json
import pickle
import os
import time

class Indexer(object):


	def __init__(self, bkpFile):
		''' load bookkeeping file no matter it is in building or loading mode '''
		self.bkp = self._load_booKeeping_from(bkpFile)


	''' Everything initialized by this method is global to this class so self.mainProcess() can use them. '''
	def _init_for_building(self, kwargs):
		''' total doc count '''
		self.tot_docs = 0

		''' init empty document indexing cache mapper, only one docMap needed with default name is 'main '''
		self.mc = self._init_mapCacher()
		self.mainDocMap = self.mc.get_docMap()

		''' this is the best part of the project No.2: the use of kwargs is maximized this way. '''
		self.index = self._init_index(kwargs)
		self.invIndex = self._init_invIdex(kwargs)
		self.docAnalyzer = DocAnalyzer(RegexpTokenizer(r'\w+'))

		return ;


	def _init_index(self, params):
		index = {}
		for k in params:
			index[k] = {}
		return index

	def _init_invIdex(self, params):
		invIndex = {}
		for k in params:
			invIndex[k] = None
		return invIndex

	def _load_booKeeping_from(self, bkpFile, mode = 'json'):
		if mode == 'json':
			with open(bkpFile, 'r') as handler:
				return json.load(handler)
		else:
			raise Exception("Error in Indexer: other mode under dev...")

	def _init_mapCacher(self):
		mc = MapCacher()
		mc.init_docMap()
		return mc

	def mainProcess(self, build_invIndex_of = None, save_docIndex_at = None, save_invIndex_at = None, **kwargs):
		if build_invIndex_of is None or save_docIndex_at is None or save_invIndex_at is None:
			raise Exception('Indexer.mainProcess(): Missing arguments.')

		print 'Start to build...'

		''' init self.tot_docs, self.mc, self.mainDocMap, self.index, self.invIndex, self.docAnalyzer '''
		self._init_for_building(kwargs)

		''' the following traversing strategy looks ugly. a separate method needed to scale the app. '''
		for root, dirs, files in os.walk(build_invIndex_of):
			for f in files:
				self.tot_docs += 1
				filepath = os.path.join(root, f)
				relapath = os.path.relpath(filepath, build_invIndex_of)

				'''  mac sys checkpoint '''
				if relapath == '.DS_Store':
					continue

				url = self.bkp[relapath] # find its corresponding url in bookkeeping
				docIdx = self.mainDocMap.next_avai_idx() # retrieve the next avaliable spot in the docMap
				doc = Document(docIdx, filepath, url) # create new Document obj with the retrieved idx
				self.mainDocMap.add(doc, docIdx) # form mapping relation

				stats = self.docAnalyzer.analyze(filepath)

				for k in kwargs:
					if kwargs[k]:
						self.index[k][docIdx] = stats[k]
					# if kwargs[k] is False:
					# 	self.index[k] = {} as it is initialized

		# self.index is an intermediate result, no need to save or restore.
		print 'Doc-Term Indexing done!'
		self.save(self.mainDocMap, save_docIndex_at, mode = 'pickle')
		print 'Doc-Idx Mapping Done!'

		for k in kwargs:
			if kwargs[k]:
				if k == 'anchor':
					self.invIndex[k] = self._invert(self.index[k], anchor = True)
				else:
					self.invIndex[k] = self._invert(self.index[k], anchor = False)

		self.save(self.invIndex, save_invIndex_at)
		print 'Token-Doc Inverted Indexing Done!'
		return ;


	def _invert(self, index, anchor):
		'''
		This function involves a few variables global to this class. It must be called during self.mainProcess().
		--------------------------------------------------------------------------------------------------------
		If anchor is False:
			Input:
				{docIdx<Int>: {url<String>: [token<String>]}}
			Output:
				{token<String>: [url1, url2, ..., url3]}

		if anchor is True:
			Input:
				{docIdx<Int>: {token<String>: term<Term>}} # where no duplicated tokens present
			Output:
				{token<String>: [Document1, Document2, ..., DocumentN]}
		'''
		inverted = {}

		if anchor:
			for docIdx, url_tokens in index.iteritems():
				for url, tokens in url_tokens.iteritems():
					for token in tokens:
						if token in inverted:
							inverted[token].add(url)
						else:
							''' ranking strategy: query comes in; relevant docs found; relevant urls found; intersect. '''
							inverted[token] = set([url]) # make sure there is no duplicated urls and provide O(1) lookup efficiency during ranking.

			return inverted

		for docIdx, tkMap in index.iteritems():
			doc = self.mainDocMap.get_item_at(docIdx) # all the tokens in mainDocMap[docIdx]
			for token in tkMap:
				term = tkMap[token]
				inv_doc = InvDocument(doc.idx, doc.filepath, doc.url, term.token, term.positions, term.tf)

				if token in inverted:
					inverted[token].append(inv_doc) # no duplicated tokens present in the same document but they do occur over a bunch of other documents
				else:
					inverted[token] = [inv_doc]

		for token in inverted:
			df = len(inverted[token])
			for inv_doc in inverted[token]:
				inv_doc.set_idf(df, self.tot_docs)

		return inverted


	'''
	Indexer.restore() help cache the inverted index result file into memory for ranking use.
	'''
	def restore(self, load_docIndex_from = None, load_invIndex_from = None):
		if load_docIndex_from is None or load_invIndex_from is None:
			raise Exception('Indexer.restore(): Missing argument.')
		self.mainDocMap = self.load(load_docIndex_from, mode = 'pickle')
		self.invIndex = self.load(load_invIndex_from, mode = 'pickle')
		print 'Data Restore Done!'
		return ;


	def load(self, filepath, mode = 'pickle'):
		if mode == 'pickle':
			with open(filepath, 'rb') as f:
				return pickle.load(f)
		elif mode == 'json':
			raise Exception('Under dev...')
		else:
			raise Exception('Error: "mode" can be either "pickle" or "json".')


	def save(self, data, filepath, mode = 'pickle'):
		if mode == 'pickle':
			with open(filepath, 'wb') as f:
				pickle.dump(data, f)
				return ;
		elif mode == 'json':
			raise Exception('Under dev...')
		else:
			raise Exception('Error: "mode" can be either "pickle" or "json".')




t = time.time()
workingDir = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/testWebpage/'
bkpFile = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/metadata/bookkeeping.json'
docIndexFile = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/metadata/docIndex.pickle'
invIndex = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/metadata/invIndex.pickle'

indexer = Indexer(bkpFile)
indexer.mainProcess(build_invIndex_of = workingDir, save_docIndex_at = docIndexFile, save_invIndex_at = invIndex, title = True, header = True, body = True, anchor = True)
print "invert indexing takes", time.time() - t
t = time.time()

indexer.restore(load_docIndex_from = docIndexFile, load_invIndex_from = invIndex)
print "restore indexing takes", time.time() - t

iiMap = indexer.invIndex
print iiMap['body']['machine']
