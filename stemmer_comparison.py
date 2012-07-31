#!/usr/bin/env python
# coding: utf-8

import sys
import os
from time import time
from glob import glob
from collections import Counter
from nltk.stem.snowball import PortugueseStemmer
from nltk.stem import PorterStemmer, LancasterStemmer, RSLPStemmer
from nltk.corpus import machado, stopwords
from index import Index


def create_indexes():
    stopwords_pt = stopwords.raw('portuguese').decode('utf-8').split('\n')[:-1]
    snowball_stemmer = PortugueseStemmer()
    rslp_stemmer = RSLPStemmer()
    indexes = {'no-stemmer-with-stopwords': Index(stemmer=None, stopwords=[]),
               'no-stemmer-without-stopwords': Index(stemmer=None, stopwords=stopwords_pt),
               'snowball-with-stopwords': Index(stemmer=snowball_stemmer, stopwords=[]),
               'snowball-without-stopwords': Index(stemmer=snowball_stemmer, stopwords=stopwords_pt),
               'rslp-with-stopwords': Index(stemmer=rslp_stemmer, stopwords=[]),
               'rslp-without-stopwords': Index(stemmer=rslp_stemmer, stopwords=stopwords_pt),}
    for index_name, index in indexes.iteritems():
        index.name = index_name
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

def load_indexes():
    indexes = []
    for filename in glob('data/*.pickle'):
        indexes.append(Index.load(filename))
    return indexes

def stem(term):
    snowball_stemmer = PortugueseStemmer()
    rslp_stemmer = RSLPStemmer()
    print u'[{}] Snowball: {}, RSLP: {}'.format(term,
            snowball_stemmer.stem(term), rslp_stemmer.stem(term))

def search(query):
    from tokenizer import tokenize

    for index in indexes:
        results = index.find(query)
        print '{} ({}):'.format(index.name, len(results))
        for result in results:
            print '  {}'.format(result)
            text = machado.raw(result)
            for token in tokenize(query):
                new_token = index.stem(token.lower())
                counter = text.lower().count(new_token)
                initial_index = 0
                for i in range(counter):
                    idx = text.lower().find(new_token, initial_index)
                    initial_index = idx + 1
                    print '    ', text[idx - 50:idx + 50].replace('\n',
                                                                  '\n    ')
                    print

def histogram(data):
    result = {}
    values = data.values()
    for value in set(values):
        result[value] = values.count(value)
    result_list = result.items()
    result_list.sort(lambda a, b: cmp(a[0], b[0]))
    return result_list

if __name__ == '__main__':
    from matplotlib import pylab

    #create_indexes()
    indexes = load_indexes()
    histograms_stemmed = []
    histograms_probability = []
    for index in indexes:
        stemmed_token_count = Counter()
        probabilities = {}
        for token, original_tokens in index._original_token.iteritems():
            for original_token in original_tokens:
                stemmed_token_count[token] += index._token_frequency[original_token]
            total = stemmed_token_count[token]
            for original_token in original_tokens:
                token_count = float(index._token_frequency[original_token])
                probabilities[original_token] = int((100 * token_count) / total)
        stemmed_token_histogram = histogram(stemmed_token_count)
        histograms_stemmed.append((index.name, stemmed_token_histogram))
        histograms_probability.append((index.name, histogram(probabilities)))

    for name, histogram in histograms_stemmed:
        x = [item[0] for item in histogram[:50]]
        y = [item[1] for item in histogram[:50]]
        pylab.plot(x, y, label=name)
    pylab.grid(True)
    pylab.legend()
    pylab.xlabel(u'Stemmed token frequency')
    pylab.ylabel(u'Frequency of frequency')
    pylab.savefig('stemmed-token-frequency.png', dpi=900)

    pylab.clf()

    for name, histogram in histograms_probability:
        x = [item[0] for item in histogram]
        y = [item[1] for item in histogram]
        pylab.plot(x, y, label=name)
    pylab.grid(True)
    pylab.legend()
    pylab.xlabel(u'Token probability')
    pylab.ylabel(u'Frequency of token probability')
    pylab.savefig('token-probability.png', dpi=900)
