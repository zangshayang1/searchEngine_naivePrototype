from flask import Flask, render_template, request
from server.ranker import Ranker

'''
Pickle is the serialization package that goes with Python.
Different from json, it can serialize Python class, such as the ones in elements module, which is quite neat in this application.
When you want to restore the data with pickle.load() like how I initialize the Ranker() object, it is required that 'elements' is in sys.modules.
If elements.py is in the server module, the above can't be done without additional effort as I did below.
Simply import server.elements is not going to help, because it only creates a 'server.elements' in sys.modules.
'''
import sys
from server import elements
sys.modules['elements'] = elements



# from django.shortcuts import render_to_response
# import os
# import sys

# path = r'C:\Users\xiaoyanqu\Documents\GitHub\Search-Engine\app'  # use your own username here
# if path not in sys.path:
#     sys.path.append(path)

# os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.py")
# from app import settings
# if settings.DEBUG:
#     print "Setting warning."


invIdx_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_invIndex.pkl'
docIdx_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_docIndex.pkl'
bookkeeping_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/bookkeeping.json'
corpus_dir = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/test_WEBPAGES_RAW/'
pageRank_file = '/Users/shayangzang/Desktop/cs211-infoRetrieval/project3/myMetadata/test_pageRank.pkl'

ranker = Ranker(invIdx_file, docIdx_file, corpus_dir, bookkeeping_file, pageRank_file)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def search():
    return render_template('search.html')


@app.route('/result', methods=['GET', 'POST'])
def show_result():
    global ranker
    # Get user's query as input named 'term'
    if request.method == 'POST':
        term = request.form['term']
    # An example of manipulating the output dictionary "out <type 'dict'>" into "res <type 'dict'>"

    out = ranker.retrieve_ranking(term)

    res = list()
    for t, u, s in zip(out['title'], out['url'], out['snippet']):
        res.append([t, u, s])
    print res
    return render_template('result.html', result=res)


if __name__ == "__main__":
    app.run(debug=True)
