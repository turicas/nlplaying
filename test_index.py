# coding: utf-8

import unittest
import cPickle
from os import unlink
from os.path import exists as file_exists
from tempfile import NamedTemporaryFile
from nltk.stem import PorterStemmer
from index import Index


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.filename = None

    def tearDown(self):
        if self.filename is not None:
            try:
                unlink(self.filename)
            except OSError:
                pass

    def test_should_add_documents_with_name_and_content(self):
        index = Index()
        index.add_document('test', 'this is my first document')
        index.add_document('test2', 'this is my second document')
        self.assertEquals(len(index), 2)
        self.assertEquals(index._documents, set(['test', 'test2']))

    def test_should_automatically_index_when_add_documents(self):
        index = Index()
        index.add_document('test', 'this is my first document')
        index.add_document('test2', 'this is my second document')
        expected_tokens = set(['this', 'is', 'my', 'first', 'second',
                               'document'])
        expected_index = {'this': set(['test', 'test2']),
                          'is': set(['test', 'test2']),
                          'my': set(['test', 'test2']),
                          'first': set(['test']),
                          'second': set(['test2']),
                          'document': set(['test', 'test2']),}
        self.assertEquals(index.tokens(), expected_tokens)
        self.assertEquals(dict(index._index), expected_index)

    def test_should_store_tokens_lowercase(self):
        index = Index()
        index.add_document('doc', 'This IS mY firsT DoCuMeNt')
        expected_tokens = set(['this', 'is', 'my', 'first', 'document'])
        expected_index = {'this': set(['doc']),
                          'is': set(['doc']),
                          'my': set(['doc']),
                          'first': set(['doc']),
                          'document': set(['doc']),}
        self.assertEquals(index.tokens(), expected_tokens)
        self.assertEquals(dict(index._index), expected_index)

    def test_should_be_able_to_find_by_term(self):
        index = Index()
        index.add_document('doc1', 'this is my first document')
        index.add_document('doc2', 'this is my second document')
        index.add_document('doc3', 'another document')
        self.assertEquals(index.find_by_term('document'),
                          set(['doc1', 'doc2', 'doc3']))
        self.assertEquals(index.find_by_term('DOCUMENT'),
                          set(['doc1', 'doc2', 'doc3']))
        self.assertEquals(index.find_by_term('this'), set(['doc1', 'doc2']))
        self.assertEquals(index.find_by_term('is'), set(['doc1', 'doc2']))
        self.assertEquals(index.find_by_term('my'), set(['doc1', 'doc2']))
        self.assertEquals(index.find_by_term('first'), set(['doc1']))
        self.assertEquals(index.find_by_term('second'), set(['doc2']))
        self.assertEquals(index.find_by_term('another'), set(['doc3']))

    def test_should_be_able_to_find_using_AND_OR_and_NOT(self):
        index = Index()
        index.add_document('doc1', 'this is my first document')
        index.add_document('doc2', 'this is my second document')
        index.add_document('doc3', 'another document')
        self.assertEquals(index.find('this document'), set(['doc1', 'doc2']))
        self.assertEquals(index.find('this another'), set())
        self.assertEquals(index.find('a b'), set())
        self.assertEquals(index.find('another'), set(['doc3']))
        self.assertEquals(index.find('first another'), set([]))

    def test_passing_stopwords_should_remove_these_words_from_token_list(self):
        index = Index(stopwords=['yes', 'no', ',', '.', '!'])
        index.add_document('coffee', 'Yes, sir! No, Joyce.')
        self.assertEquals(index._index, {'sir': set(['coffee']),
                                         'joyce': set(['coffee'])},)

    def test_passing_a_stemmer_should_index_tokens_stemmed(self):
        porter_stemmer = PorterStemmer()
        index = Index(stemmer=porter_stemmer)
        index.add_document('coffee', 'I liked it')
        self.assertEquals(index._index, {'i': set(['coffee']),
                                         'like': set(['coffee']),
                                         'it': set(['coffee'])},)
        index = Index(stemmer=None)
        index.add_document('coffee', 'I liked it')
        self.assertEquals(index._index, {'i': set(['coffee']),
                                         'liked': set(['coffee']),
                                         'it': set(['coffee'])},)

    def test_passing_a_stemmer_should_stem_search_term_before_matching(self):
        porter_stemmer = PorterStemmer()
        index = Index(stemmer=porter_stemmer)
        index.add_document('coffee', 'I liked it')
        self.assertEquals(index.find_by_term('liked'), set(['coffee']))

    def test_calling_method_dump_should_pickle_the_index_object(self):
        fp = NamedTemporaryFile(delete=False)
        fp.close()
        self.filename = fp.name
        index = Index()
        index.add_document('coffee', 'I liked it')
        index.add_document('water', 'I need it')
        index.dump(self.filename)
        self.assertTrue(file_exists(self.filename))
        fp = open(self.filename)
        retrieved_index = cPickle.load(fp)
        self.assertEquals(len(retrieved_index), 2)
        self.assertEquals(set(retrieved_index._index.keys()),
                          set(['i', 'liked', 'need', 'it']))

    def test_calling_method_load_should_retrieve_object_from_pickle_file(self):
        fp = NamedTemporaryFile(delete=False)
        fp.close()
        self.filename = fp.name
        index = Index()
        index.add_document('coffee', 'I liked it')
        index.add_document('water', 'I need it')
        index.dump(self.filename)
        retrieved_index = Index.load(self.filename)
        self.assertEquals(len(retrieved_index), 2)
        self.assertEquals(set(retrieved_index._index.keys()),
                          set(['i', 'liked', 'need', 'it']))
