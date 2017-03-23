'''
This module implemented two classes:
    AuthorityTable - facilitate the incrementation of urls' authorities, refer to indexer.py for detailed usage
    PageRank - facilitate the computation of page rank score
'''



class AuthorityTable(object):
    '''
    Input:
        List<urls> from bkpfile
    '''
    def __init__(self, bkp_urls):
        self._authorityMap = dict((url, 0) for url in bkp_urls)

    def increment_authority_for(self, url):
        if not url in self._authorityMap:
            return ;
        self._authorityMap[url] += 1
        return ;

    def increment_authorities_for(self, urls):
        for url in urls:
            self.increment_authority_for(url)
        return ;

    def get_authority_of(self, url):
        if not url in self._authorityMap:
            raise Exception("Error in AuthorityTable() class: Can't find the url in map.")
        return self._authorityMap[url]

    def get_table(self):
        return self._authorityMap



class PageRank():
    ''' PageRank() is an independent class, shouldn't be built as to depend on some other class. '''
    def __init__(self, dampen_factor = 0.85):
        self.dampen_factor = dampen_factor


    def process(self, outlinkMap = None, iterations = 8):
        '''
            Input:
                outlinkMap - Dict<url : List<outgoing_links>>, already filtered.
            Output:
                nextPR - Dict<url : page rank score> after a number of iterations.
        '''
        if outlinkMap is None:
            raise Exception('Error in PageRank(): outlinkMap must be provided.')

        prevPR = dict((u, 0) for u in outlinkMap)
        nextPR = dict((k, 1) for k in outlinkMap)

        for _ in range(iterations):
            for root_url in outlinkMap:
                prevPR[root_url] = nextPR[root_url] # update previous pagerank score

            for root_url in outlinkMap:
                outgoing_links = outlinkMap[root_url]
                hubness = len(outgoing_links)
                for url in outgoing_links:
                    nextPR[url] += self.dampen_factor * prevPR[url] / float(hubness) # compute next pagerank score based on previous ones.
                nextPR[root_url] += 1 - self.dampen_factor

        return nextPR
