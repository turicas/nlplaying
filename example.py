#!/usr/bin/env python
# coding: utf-8
# Tip: run this script with `python -i example.py`
# (or `ipython -i example.py`), so you can interactively do searches by
# executing: `my_index.search('...search terms...')`

from nltk.corpus import machado
from index import Index


print 'Creating index...'
my_index = Index()
filenames = machado.fileids()[50:]
for filename in filenames:
    my_index.add_document(filename, machado.raw(filename))

print 'Searching...'
print my_index.find('brasil azul')
