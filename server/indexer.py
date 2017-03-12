from docAnalyzer import DocAnalyzer
from nltk.tokenize import RegexpTokenizer

import elements
from elements import Document, MapCacher, InvDocument, IdxItemMap

import pickle
import json
import os

class Indexer(object):


	def __init__(self, build_invIndex_of = None, bkp_file = None, **kwargs):
		if build_invIndex_of is None:
			raise Exception("MissingArg: 'build_invIndex_of' must be provided (The dir containing crawled corpus).")
		if bkp_file is None:
			raise Exception("MissingArg: 'bkp_file' must be provided (The file containing corpus page urls).")

		self.workingDir = build_invIndex_of

		self.bkp = self._load(bkp_file, mode = 'json') # mode = bkp_file.split('.')[-1] makes it more flexible, NOT necessary for the scope of this project.
		self.pr = dict((self.bkp[k], 0) for k in self.bkp) # for collecting page rank count
		self.tot_docs = len(self.pr)

		self.mc = MapCacher() # MapCacher is an abstract layer that is beyond the scope of this project
		self.mc.init_docMap(name = 'main') # you can create and name a mapping data structure within self.mc
		self.mainDocMap = self.mc.get_docMap(name = 'main') # assign another variable to the created mapping data structure for easy access.

		# only one docMap will be used but I still keep this layer for scale purpose.

		self.index = self._init_kwargs_indexing_structure(kwargs) # this is also a highlight because: 1. the use of kwargs is maximized this way.
		self.invIndex = self._init_kwargs_indexing_structure(kwargs) # 2. eventually there should be one invIndexing table for one kwarg, that points to a unique tag type of html info.

		self.docAnalyzer = DocAnalyzer(RegexpTokenizer(r'\w+'))


	def _init_kwargs_indexing_structure(self, params):
		index = {}
		for k in params:
			index[k] = {}
		return index


	def _load(self, filepath, mode = 'json'):
		if not os.path.exists(filepath):
			raise Exception("MissingFile: {} doens't exist.".format(filepath))

		if mode == 'json':
			with open(filepath, 'r') as handler:
				return json.load(handler)
		else:
			raise Exception("Error in Indexer: other mode under dev...")


	def mainProcess(self, save_docIndex_at = None, save_invIndex_at = None, save_pageRank_at = None):
		if save_docIndex_at is None or save_invIndex_at is None or save_pageRank_at is None:
			raise Exception('Indexer.mainProcess(): Missing arguments.')

		print 'Start to build...'

		''' the following traversing strategy looks ugly. a separate method needed to scale the app. '''
		for root, dirs, files in os.walk(self.workingDir):
			for f in files:
				filepath = os.path.join(root, f)
				relapath = os.path.relpath(filepath, self.workingDir)

				''' progress indicator '''
				print relapath

				'''  mac sys checkpoint '''
				if relapath == '.DS_Store':
					continue

				url = self.bkp[relapath] # find its corresponding url in bookkeeping
				docIdx = self.mainDocMap.next_avai_idx() # retrieve the next avaliable spot in the docMap
				doc = Document(docIdx, filepath, url) # create new Document obj with the retrieved idx
				self.mainDocMap.add(doc, docIdx) # form mapping relation

				stats = self.docAnalyzer.analyze(filepath, url)

				for tag in self.index:
					self.index[tag][docIdx] = stats[tag]
					if tag == 'anchor':
						self._rank_pages(stats[tag]) # stats['anchor'] is the urls referred by the current page.

		self.save(self.pr, save_pageRank_at, mode = 'pickle')
		print 'PageRank is done!'

		self.save(self.mainDocMap, save_docIndex_at, mode = 'pickle') # self.mainDocMap itself is not json serializable.
		print 'Doc-Idx Mapping Done!'

		for tag in self.invIndex:
			if tag == 'anchor':
				self.invIndex[tag] = self._invert(self.index[tag], anchor = True)
			else:
				self.invIndex[tag] = self._invert(self.index[tag], anchor = False)

		self.save(self.invIndex, save_invIndex_at, mode = 'pickle')
		print 'Token-Doc Inverted Indexing Done!'

		return ;


	''' This function count the frequency of the given list of urls and add the information to self.pr
	Input:
		urls : List<String>
	Output:
		None
	'''
	def _rank_pages(self, urls):
		for url in urls:
			if url in self.pr:
				self.pr[url] += 1
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

			''' progress indocator '''
			print "invert doc number: {}".format(docIdx)

			doc = self.mainDocMap.get_item_at(docIdx) # all the tokens in mainDocMap[docIdx]
			for token in tkMap:
				term = tkMap[token]
				inv_doc = InvDocument(doc.idx, doc.filepath, doc.url, term.token, term.positions, term.tf)

				if token in inverted:
					inverted[token].append(inv_doc) # no duplicated tokens present in the same document but they do occur over a bunch of other documents
				else:
					inverted[token] = [inv_doc]

		''' progress indicator '''
		print "final inverting ..."

		for token in inverted:
			df = len(inverted[token])
			for inv_doc in inverted[token]:
				inv_doc.set_idf(df, self.tot_docs)

		return inverted


	def save(self, data, filepath, mode = 'json'):
		if mode == 'json':
			with open(filepath, 'w') as f:
				json.dump(data, f)
		elif mode == 'pickle':
			with open(filepath, 'wb') as f:
				pickle.dump(data, f)
		else:
			raise Exception('Error: "mode" can be either "pickle" or "json".')



if __name__ == '__main__':

	import time

	t = time.time()

	''' Input Format: workingDir is a directory containing page.html only. Children dir are allowed. '''
	workingDir = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/test_WEBPAGES_RAW/'

	''' Input Format: bkp_file contains a dictionary -> {relative filepath : absolute url} '''
	bkp_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/bookkeeping.json'

	docIndexFile = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_docIndex.pkl'
	invIndex = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_invIndex.pkl'
	pageRank_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_pageRank.pkl'

	indexer = Indexer(build_invIndex_of = workingDir, bkp_file = bkp_file, title = True, header = True, body = True, anchor = True)

	indexer.mainProcess(save_docIndex_at = docIndexFile, save_invIndex_at = invIndex, save_pageRank_at = pageRank_file)

	print "invert indexing takes", time.time() - t

	# t = time.time()
	#
	# indexer.restore(load_docIndex_from = docIndexFile, load_invIndex_from = invIndex)
	# print "restore indexing takes", time.time() - t

	# iiMap = indexer.invIndex
	# print iiMap['body']['machine']
