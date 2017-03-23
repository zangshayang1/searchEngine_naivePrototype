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


bkp_file = config.BOOKKEEPING_FILE
corpus_dir = config.WORKING_DIR

invIndex_file = config.INVINDEX_FILE
pageMap_file = config.PAGEMAP_FILE

ranker = Ranker(corpus_dir, bkp_file, invIndex_file, pageMap_file)

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
