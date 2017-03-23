import config
from docAnalyzer import DocAnalyzer
from nltk.tokenize import RegexpTokenizer
from utils import PageRank, AuthorityTable

import elements
from elements import Document, MapCacher, InvDocument, IdxItemMap, URL

import pickle
import json
import os
import time

class Indexer(object):

	def __init__(self, build_invIndex_of = None, bkp_file = None, **kwargs):
		print 'Initializing ... {}'.format(time.time())

		if build_invIndex_of is None:
			raise Exception("MissingArg: 'build_invIndex_of' must be provided (The dir containing crawled corpus).")
		if bkp_file is None:
			raise Exception("MissingArg: 'bkp_file' must be provided (The file containing corpus page urls).")

		'''
		Basic input relevant to the Indexer.
			workingDir - corpus dir
			bkp - bookkeeping Dict<relative filepath string : absolute url string>
			tot_docs - total count of the documents '''
		self.workingDir = build_invIndex_of
		self.bkp = self._load(bkp_file, mode = 'json') # mode = bkp_file.split('.')[-1] makes it more flexible, NOT necessary for the scope of this project.
		self.tot_docs = len(self.bkp)

		'''
		To construct a mapping relation between url and corresponding URL() obj
			urlMap - Dict<url string : URL obj>, behind URL obj there is a directed graph of the mapping relation among the urls from the corpus '''
		self.urlMap = dict((self.bkp[k], None) for k in self.bkp) # for mapping current page url the corresponding URL obj


		'''
		To construct two mapping relations within the pageMap - Dict<key string : Dict<>>
			1. mainDocMap - Dict<idx Int : Document obj>
			2. urlDocMap - Dict<url string : idx Int> '''
		self.pageMap = MapCacher() # MapCacher is an abstract layer that is beyond the scope of this project
		self.pageMap.init_docMap(key = 'idx') # you can create and name, with "key", a mapping data structure within self.pageMap
		self.mainDocMap = self.pageMap.get_docMap(key = 'idx') # assign another variable to the created mapping data structure for easy access.
		self.pageMap.init_docMap(key = 'url') # so you can map each url to the document
		self.urlDocMap = self.pageMap.get_docMap(key = 'url')

		'''
		To init storage data structure for indexing/invert indexing purpose
			index - Dict<kwarg : Dict<docIdx : stats from docAnalyzer>>
			invIndex - Dict<kwarg : Dict<token string : Document obj>> '''
		self.index = self._init_kwargs_indexing_structure(kwargs) # this is also a highlight because: 1. the use of kwargs is maximized this way.
		self.invIndex = self._init_kwargs_indexing_structure(kwargs) # 2. eventually there should be one invIndexing table for one kwarg, that points to a unique tag type of html info.


	def mainProcess(self, save_pageMap_at = None, save_invIndex_at = None):
		if save_pageMap_at is None or save_invIndex_at is None:
			raise Exception('Indexer.mainProcess(): Missing arguments.')

		print 'Start to build...{}'.format(time.time())

		''' authorityTable - AuthorityTable() obj defined in utils.py, store and increment authorities '''
		authorityTable = AuthorityTable([self.bkp[k] for k in self.bkp])
		# Two reasons I made authorityTable an independent class in utils.py instead of just a plain dictionary
		# 	1. It is a temporary storage where pages increment their authorities and thus better to set local to mainProcess().
		# 	2. It is an iterative process unlike pages' hubness, which only require calling len(outgoing_links) once for per page.
		# 	   Therefore, it's better to make it an independent class that can increment itself, rather than passing the dictionary over and over again to some function call.

		''' pr - PageRank() obj, get ready for filtering and computing page rank score '''
		pr = PageRank(dampen_factor = 0.85)

		''' docAnalyzer - DocAnalyzer() obj defined in docAnalyzer.py, parsing html files '''
		docAnalyzer = DocAnalyzer(RegexpTokenizer(r'\w+'))

		print '\t Mapping pages ... {}'.format(time.time())
		for root, dirs, files in os.walk(self.workingDir):
			for f in files:
				filepath = os.path.join(root, f)
				relapath = os.path.relpath(filepath, self.workingDir)
				# bypassing this mac sys signature file
				if relapath == '.DS_Store': continue

				root_url = self.bkp[relapath] # find its corresponding abs url in bookkeeping
				docIdx = self.mainDocMap.next_avai_idx() # retrieve the next avaliable spot in the docMap
				doc = Document(docIdx, filepath, root_url) # create new Document obj with the retrieved idx/root_url/filepath
				self.mainDocMap.add(doc) # indexing the doc by default self._idx defined in IdxItemMap() class in elements.py
				self.urlDocMap.add(docIdx, key = root_url) # mapping the root_url with the document idx for later use. Didn't map it with Document obj because it saves space this way.
				self.urlMap[root_url] = URL(root_url) # prepare urlMap - Dict<root_url : URL> for computing pageRank scores

		print '\t Parsing pages ... {}'.format(time.time())
		for docIdx, doc in self.mainDocMap.iteritems():
			# retrieve parsed results from docAnalyzer.analyze()
			filepath, root_url = doc.filepath, doc.url
			# progress indicator
			print '\t', filepath

			stats = docAnalyzer.analyze(filepath, root_url)
			for tag in self.index:
				if tag == 'anchor':
					# stats['anchor'] is the Dic<outgoing_url : List<anchorTokens>> referred by the current page.
					stats[tag] = dict((elements.toAbsUrl(root_url, u), set(stats[tag][u])) for u in stats[tag])  # update stats['anchor'] with abs urls replacing relative urls
					filtered_outgoing_links = [u for u in stats[tag] if u in self.urlMap] # filter those outgoing links that are not in the corpus urls
					authorityTable.increment_authorities_for(filtered_outgoing_links) # authorityTable is only within the scope of the mainProcess()
					self.urlMap[root_url].add(outgoing_links = set(filtered_outgoing_links)) # type cast to set, union operation defined in URL() class, for scalability
					for link in filtered_outgoing_links:
						self.urlMap[link].add(anchorTokens = stats[tag][link])
				self.index[tag][docIdx] = stats[tag]
		print '\t Done!'

		print '\t Computing pageRank, hubness and authority ... {}'.format(time.time())
		pr_results = pr.process(outlinkMap = dict((url, self.urlMap[url].outgoing_links) for url in self.urlMap), iterations = 8)
		for url in self.urlMap:
			docIdx = self.urlDocMap.get_item_at(url)
			doc = self.mainDocMap.get_item_at(docIdx)
			doc.set(
					pagerank = pr_results[url], # pr_results - Dict<url: score> is a returned result from pr.process()
					hubness = len(self.urlMap[url].outgoing_links), # hubness comes from the filtered urlMap - Dict<url: URL obj>
					authority = authorityTable.get_authority_of(url) # authorityTable - Class AuthorityTable() is a temp storage to conveniently increment urls' authorities.
					)

		self.save(self.pageMap, save_pageMap_at, mode = 'pkl') # self.mainDocMap itself is not json serializable.
		print '\t Done! Saved.'

		print '\t Inverting ... {}'.format(time.time())
		for tag in self.invIndex:
			print '\t\t', tag
			self._invert(tag)

		self.save(self.invIndex, save_invIndex_at, mode = 'pkl')
		print '\t Done! Saved.'

		print 'Successful! {}'.format(time.time())
		return ;


	def _invert(self, tag):
		'''
		This function implements the inverted indexing process
			Input:
				tag - one of the following: title, header, body, anchor
			Output:
				None '''

		# NOTE: invert indexing anchor tokens is very different from invert indexing three other parts
		# 		the major difference comes from the fact that within the scope of this project,
		# 		we didn't "Terminize" anchor tokens and thus same Document() objs essentially the same thing regardless that
		# 		it is invertedly indexed by different tokens. But during indexing the other three parts,
		# 		different InvDocument() objs are created to preserve the additional info, such as tf and positions.
		if tag == 'anchor':
			for url in self.urlMap:
				url_obj = self.urlMap[url]
				docIdx = self.urlDocMap.get_item_at(url)
				for tk in url_obj.anchorTokens:
					# all the non-repeated anchor tokens that point to the url, whose corresponding doc will not occur again
					if tk in self.invIndex[tag]:
						self.invIndex[tag][tk].append(docIdx)
					else:
						self.invIndex[tag][tk] = [docIdx]
			return ;

		for docIdx, tkMap in self.index[tag].iteritems():
			doc = self.mainDocMap.get_item_at(docIdx) # all the tokens in mainDocMap[docIdx]
			for tk in tkMap:
				term = tkMap[tk]
				inv_doc = InvDocument(doc.idx, doc.filepath, doc.url, term.token, term.positions, term.tf)

				if tk in self.invIndex[tag]:
					# no duplicated tokens present in the same document but they do occur over a bunch of other documents
					self.invIndex[tag][tk].append(inv_doc)
				else:
					self.invIndex[tag][tk] = [inv_doc]

		for tk in self.invIndex[tag]:
			df = len(self.invIndex[tag][tk])
			for inv_doc in self.invIndex[tag][tk]:
				inv_doc.set_idf(df, self.tot_docs)

		return ;

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
		elif mode == 'pkl':
			with open(filepath, 'rb') as handler:
				return pickle.load(handler)
		else:
			raise Exception("Error in Indexer: other mode under dev...")

	def save(self, data, filepath, mode = 'json'):
		if mode == 'json':
			with open(filepath, 'w') as f:
				json.dump(data, f)
		elif mode == 'pkl':
			with open(filepath, 'wb') as f:
				pickle.dump(data, f)
		else:
			raise Exception('Error: "mode" can be either "pickle" or "json".')



if __name__ == '__main__':

	t = time.time()

	''' Input Format: workingDir is a directory containing page.html only. Children dir are allowed. '''
	workingDir = config.WORKING_DIR

	''' Input Format: bkp_file contains a dictionary -> {relative filepath : absolute url} '''
	bkp_file = config.BOOKKEEPING_FILE

	pageMapFile = config.PAGEMAP_FILE
	invIndex = config.INVINDEX_FILE

	indexer = Indexer(build_invIndex_of = workingDir, bkp_file = bkp_file, title = True, header = True, body = True, anchor = True)

	indexer.mainProcess(save_pageMap_at = pageMapFile,
						save_invIndex_at = invIndex
						)

	print "Total Time: {}".format(time.time() - t)
