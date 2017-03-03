from elements import IndexStructure
from DocAnalyzer import DocAnalyzer


from element import Document, MapCacher
import os
import json

class Indexer(object):

	"""
	If webpages come in in batches. Given the root dir of this batch of data, Indexer() take care of it.
	"""
	def __init__(self, dir):
		self.dir = dir
		self.bk = None
		self.mainIndex = {}

	def load_booKeeping_from(filepath, mode = 'json'):
		if mode == 'json':
			with open(filepath, 'r') as handler:
				self.bk = json.load(handler)
				return ;
		else:
			raise Exception("Error in Indexer: other mode under dev...")

	def _init_mapCacher(self):
		mc = MapCacher()
		mc.init_docMap('main')
		mc.init_termMap('title')
		mc.init_termMap('header')
		mc.init_termMap('body')
		return mc

	def mainProcess(self):
		mc = self._init_mapCacher():

		for root, dirs, files in os.walk(self.dir):
			for f in files:
				filepath = os.path.join(root, f)
				relapath = os.path.relpath(filepath, self.dir)
				url = self.bk[relapath]

				mainDoc = mc.docMap['main']
				docIdx = mainDoc.get_next_count() # for future reference via docNum int
				doc = Document(docIdx, filepath, url) # create new Document obj
				mainDoc.add_new(doc) # form mapping relation

				tk_dict = newDoc.tokenize() # tokenization

				"""
				when query comes in as a stream of strings, 3 indexing dictionaries
				with term strings as keys are needed for quick reference. Thus, 3 mapping relations are needed in MapCaher. Name each sub dictionary a name.

				"""

	def invert(self):
		pass













class yIndexer():

	def __init__(self):
		self.analyer = DocAnalyzer()

	def processing(self, directory):
		with open('test.json', "r") as f:
			data = json.load(f)
			for root, dirs, files in os.walk(directory):
				for file in files:
					path = os.path.join(root, file)
					rel_path = os.path.relpath(path, directory)
					print rel_path
					title, content = self.analyer.extractData(path)
					tokens = self.analyer.tokenize(content)
					title_tokens = self.analyer.tokenize(title)
					token_position = self.analyer.token_with_position(tokens)
					title_token_position = self.analyer.token_with_position(title_tokens)
					token_freq = self.analyer.frequency(token_position)
					title_token_freq = self.analyer.frequency(title_token_position)
					token_tf = self.analyer.tf(token_freq)


					for token in token_freq.keys():
						if data.has_key(token):
							data[token]['df'] += 1
							data[token]['idf'] = self.analyer.idf(data[token]['df'])
							if token in title_tokens:
								data[token]['docs'][rel_path] = {"tf": token_tf[token], "pos":token_position[token], "title_pos": title_token_position[token]}
							else:
								data[token]['docs'][rel_path] = {"tf": token_tf[token], "pos":token_position[token], "title_pos": []}
						else:
							df = 1
							idf = self.analyer.idf(df)
							filename = rel_path
							pos = token_position[token]
							tf = token_tf[token]
							if token in title_tokens:
								title_pos = title_token_position[token]
							else:
								title_pos = []
							args = [df, idf, filename, tf, pos, title_pos]
							index = IndexStructure(args)
							structure = index.structure
							data[token] = structure

		with open('test.json', 'w') as f:
			json.dump(data, f, indent=2)


directory = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/WEBPAGES_RAW'

testing = Indexer()
testing.processing(directory)
