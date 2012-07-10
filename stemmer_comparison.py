#!/usr/bin/env python
# coding: utf-8

import sys
import os
from time import time
from nltk.stem.snowball import PortugueseStemmer
from nltk.stem import PorterStemmer, LancasterStemmer, RSLPStemmer
from nltk.corpus import machado, stopwords
from index import Index


def create_indexes():
    stopwords_pt = stopwords.raw('portuguese').decode('utf-8').split('\n')[:-1]
    snowball_stemmer = PortugueseStemmer()
    porter_stemmer = PorterStemmer()
    lancaster_stemmer = LancasterStemmer()
    rslp_stemmer = RSLPStemmer()
    indexes = {'no-stemmer-with-stopwords': Index(stemmer=None, stopwords=[]),
               'no-stemmer-without-stopwords': Index(stemmer=None, stopwords=stopwords_pt),
               'snowball-with-stopwords': Index(stemmer=snowball_stemmer, stopwords=[]),
               'snowball-without-stopwords': Index(stemmer=snowball_stemmer, stopwords=stopwords_pt),
               'porter-with-stopwords': Index(stemmer=porter_stemmer, stopwords=[]),
               'porter-without-stopwords': Index(stemmer=porter_stemmer, stopwords=stopwords_pt),
               'lancaster-with-stopwords': Index(stemmer=lancaster_stemmer, stopwords=[]),
               'lancaster-without-stopwords': Index(stemmer=lancaster_stemmer, stopwords=stopwords_pt),
               'rslp-with-stopwords': Index(stemmer=rslp_stemmer, stopwords=[]),
               'rslp-without-stopwords': Index(stemmer=rslp_stemmer, stopwords=stopwords_pt),}
    filenames = machado.fileids()
    index_count = len(indexes)
    total_iterations = len(filenames) * index_count
    counter = 1
    for filename in filenames:
        contents = machado.raw(filename)
        for index_name, index in indexes.iteritems():
            info = '[{:05d}/{:05d}] Adding document "{}" to index "{}" ... '\
                    .format(counter, total_iterations, filename, index_name)
            sys.stdout.write(info)
            start = time()
            index.add_document(filename, contents)
            end = time()
            sys.stdout.write('OK ({:09.5f}s)\n'.format(end - start))
            counter += 1

    if not os.path.exists('data'):
        os.mkdir('data')
    counter = 1
    for index_name, index in indexes.iteritems():
        info = '[{:02d}/{:02d}] Dumping index "{}" ... '.format(counter,
                index_count, index_name)
        sys.stdout.write(info)
        start = time()
        index.dump('data/{}.pickle'.format(index_name))
        end = time()
        sys.stdout.write('OK ({:09.5f}s)\n'.format(end - start))
        counter += 1


if __name__ == '__main__':
    create_indexes()
