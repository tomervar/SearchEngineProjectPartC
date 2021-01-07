import math

# you can change whatever you want in this module, just make sure it doesn't
# break the searcher module
class Ranker:
    def __init__(self, indexer):
        self.indexer = indexer


    @staticmethod
    def rank_relevant_docs(relevant_docs, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        return [d[0] for d in ranked_results]

    def rank_tf_idf_query(self, query_as_dict, query_len):
        query_term_weights_dict = {}
        for term in query_as_dict:
            if term not in self.indexer.inverted_idx:
                continue
            tf = query_as_dict[term]/query_len
            idf = self.indexer.inverted_idx[term][1]
            w_iq = tf * idf
            query_term_weights_dict[term] = w_iq
        return query_term_weights_dict

    def calculate_cos_sim(self, query_term_weights_dict, term_in_docs_tuple_list, doc_id):
        inner_product = 0
        segma_w_iq_pow = 0
        for term in query_term_weights_dict:
            w_iq = query_term_weights_dict[term]
            for tuple_term in term_in_docs_tuple_list:
                if tuple_term[0] == term:
                    w_ij = tuple_term[1]
                    inner_product += w_ij * w_iq
                    break
            segma_w_iq_pow += math.pow(w_iq, 2)

        doc_sqrt_segma_wij_pow = self.indexer.weight_of_docs[doc_id]
        sqrt_segma_w_iq_pow = math.sqrt(segma_w_iq_pow)

        cos_sim_normalization = doc_sqrt_segma_wij_pow * sqrt_segma_w_iq_pow
        cos_sim = inner_product/cos_sim_normalization
        return cos_sim

