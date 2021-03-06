import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import collections
import utils


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:
    """
    in this search engine we send to spelling correction and wordNet methods
    """
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None
        self.number_of_documents_in_corpus = 0

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            self.number_of_documents_in_corpus += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)

        # handle the case of capital letters according to partA rules.
        self._indexer.handle_capital_letters(self._parser)

        self._indexer.add_idf_to_inverted_index(self.number_of_documents_in_corpus)
        # build dict of {doc_id : sqrt(w_ij^2) ...}
        self._indexer.build_weight_of_docs()

        self._indexer.remove_all_the_term_with_1_appearance()

        # sort the inverted index and postiong dicts in alphabet order
        self._indexer.inverted_idx = collections.OrderedDict(sorted(self._indexer.inverted_idx.items()))
        self._indexer.postingDict = collections.OrderedDict(sorted(self._indexer.postingDict.items()))
        # print('Finished parsing and indexing.')
        # self._indexer.save_index("idx_bench")

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and 
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        searcher.set_spelling_correction()
        searcher.set_wordNet()

        return searcher.search(query)


