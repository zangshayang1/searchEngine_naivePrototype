#!/bin/bash/python

import os
import sys
from collections import defaultdict

class WordCount(object):
    """
    WordCount class takes in an opened readable file with size that fits in memory
                    tokenizes alphaNumeric characters separated by non-alphaNumeric characters
                    counts their occurrences
                    outputs sorted <token, occurrence> results
    """
    def __init__(self, readable):
        self.readable = readable

    def _alphaNumeric(self, char):
        """
        @ input: char
        @ return: bool if char is alphaNumeric or not
        """
        if 48 <= ord(char) <= 57 or 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122:
            return True
        else:
            return False

    def _tokenize(self, readable):
        """
        @ input: an opened readable
        @ outputs: List<token> collected line by line from the readable
        """
        token_stream = []
        for line in readable:
            i = 0
            l = len(line)
            while i < l:

                while i < l and not self._alphaNumeric(line[i]):
                    i += 1
                start = i
                # now start ptr to the first occurrence of alphaNumeric

                while i < l and self._alphaNumeric(line[i]):
                    i += 1
                end = i
                # now end ptr to the first occurence of non-alphaNumeric after start

                tk = line[start : end].lower()
                if tk != "":
                    token_stream.append(tk)

        return token_stream

    def _countTokens(self, token_stream):
        """
        @ input: List<token> from self._tokenize()
        @ output: HashMap<token, occurence>
        """
        tk_map = {}
        # print token_stream
        for tk in token_stream:
            if tk in tk_map:
                tk_map[tk] += 1
            else:
                tk_map[tk] = 1
        return tk_map

    def computeWordsFrequencies(self):
        """
        this method executes self._tokenize() and self._countTokens()
                    returns List<(token, occurence)> sorted by occurrences in descent
        """
        token_stream = self._tokenize(self.readable)
        token_map = self._countTokens(token_stream)
        # print token_map.items()
        return sorted(token_map.items(), key = lambda x : x[1], reverse = True)

    def mapWordsFrequencies(self):
        """
        this method executes self._tokenize() and self._countTokens()
                    returns HashMap<token, occurrence> from self._countTokens()
        """
        token_stream = self._tokenize(self.readable)
        token_map = self._countTokens(token_stream)
        return token_map

    def output_to(self, writable):
        """
        @ this methods takes in an opened writable
                       executes self.computeWordsFrequencies()
                       outputs the sorted results to file.
        """
        tk_rank = self.computeWordsFrequencies()
        l = len(tk_rank)
        output = [None for _ in range(l)]
        counter = 0
        while counter < l:
            line = tk_rank[counter][0] + ', ' + str(tk_rank[counter][1]) + '\n'
            output[counter] = line
            counter += 1
        print counter, " entries written."
        writable.write(''.join(output))
        return counter

def main():
    ifilepath = sys.argv[1]
    ofilepath = sys.argv[2]
    assert os.path.exists(ifilepath), "ERROR: input doesn't exists."
    assert os.path.exists(ofilepath), "ERROR: output already exists."
    readable = open(ifilepath, 'r')
    writable = open(ofilepath, 'w')
    wc = WordCount(readable)
    wc.output_to(writable)
    readable.close()
    writable.close()
    return 0;

if __name__ == '__main__':
    main()
