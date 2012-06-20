# coding: utf-8

from re import compile as regexp_compile
from collections import defaultdict
from tokenizer import tokenize


regexp_bool = regexp_compile(' (AND|OR) ')

class Index(object):
    def __init__(self):
        self.documents = set([])
        self.index = defaultdict(lambda: set())

    def __len__(self):
        return len(self.documents)

    def tokens(self):
        return set(self.index.keys())

    def add_document(self, name, contents):
        self.documents.update([name])
        for token in tokenize(contents):
            self.index[token.lower()].update([name])
            #TODO: create a method to process term

    def find_by_term(self, term):
        return self.index[term.lower()]
        #TODO: create a method to process term

    def find(self, terms):
        index = self.index
        documents = self.documents
        terms = regexp_bool.split(terms)
        result = []
        for term in terms:
            if term.startswith('NOT '):
                term = documents - index[term[4:].lower()]
                #TODO: create a method to process term
            elif term not in ('AND', 'OR'):
                term = index[term.lower()]
            result.append(term)
        while len(result) > 1:
            before, operator, after = result[:3]
            if operator == 'AND':
                operation_result = before & after
            elif operator == 'OR':
                operation_result = before | after
            result[:3] = [operation_result]
        return result[0]
