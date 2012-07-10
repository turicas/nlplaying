# coding: utf-8

from collections import defaultdict
from tokenizer import tokenize


class Index(object):
    def __init__(self, stemmer=None, stopwords=None):
        self._documents = set([])
        self._index = defaultdict(lambda: set())
        self._stemmer = stemmer
        if stopwords is None:
            stopwords = []
        self._stopwords = stopwords

    def __len__(self):
        return len(self._documents)

    def tokens(self):
        return set(self._index.keys())

    def stem(self, token):
        if self._stemmer is not None:
            return self._stemmer.stem(token)
        else:
            return token

    def add_document(self, name, contents):
        self._documents.update([name])
        #TODO: add ability to change tokenizer
        for token in tokenize(contents):
            lowered_token = token.lower()
            if lowered_token not in self._stopwords:
                stemmed_token = self.stem(lowered_token)
                self._index[stemmed_token].update([name])

    def find_by_term(self, term):
        lowered_term = term.lower()
        stemmed_term = self.stem(lowered_term)
        return self._index[stemmed_term]

    def find(self, terms):
        results = self._documents.copy()
        #TODO: add ability to change tokenizer
        for term in tokenize(terms):
            results &= self.find_by_term(term)
        return results
