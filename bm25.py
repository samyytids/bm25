from time import time

import psycopg2
import tiktoken

import numpy as np
from collections import Counter
import tiktoken

class BM25:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.k1 = k1  # Term frequency scaling factor
        self.b = b    # Length normalization factor
        self.documents = documents
        self.doc_count = len(documents)
        self.avg_doc_length = self._average_document_length()
        self.doc_freqs = self._calculate_doc_frequencies()

    def _average_document_length(self):
        total_length = sum(len(doc) for doc in self.documents)
        return total_length / self.doc_count

    def _calculate_doc_frequencies(self):
        doc_freqs = Counter()
        for doc in self.documents:
            unique_terms = set(doc)
            for term in unique_terms:
                doc_freqs[term] += 1
        return doc_freqs

    def _bm25_score(self, term, doc):
        term_freq = doc.count(term)
        if term_freq == 0:
            return 0.0

        idf = np.log((self.doc_count - self.doc_freqs[term] + 0.5) /
                     (self.doc_freqs[term] + 0.5) + 1)

        numerator = term_freq * (self.k1 + 1)
        denominator = term_freq + self.k1 * (1 - self.b + self.b * (len(doc) / self.avg_doc_length))

        return idf * (numerator / denominator)

    def get_scores(self, query):
        scores = np.zeros(self.doc_count)
        for term in query:
            for i, doc in enumerate(self.documents):
                scores[i] += self._bm25_score(term, doc)
        return scores

# # Example usage
# tokenizer = tiktoken.get_encoding("gpt2")  # You can choose the appropriate encoding

# # Sample text documents
# raw_documents = [
#     "The cat sat on the mat.",
#     "The dog sat on the log.",
#     "The cat and the dog are friends."
# ]

# # Tokenize the documents
# documents = [tokenizer.encode(doc) for doc in raw_documents]

# bm25 = BM25(documents)
# query = tokenizer.encode("the cat")
# scores = bm25.get_scores(query)

# for i, score in enumerate(scores):
#     print(f"Document {i}: Score = {score:.4f}")

if __name__ == "__main__":
    s = time()
    conn = psycopg2.connect(
        port = 5432, 
        dbname="rightmove_new",
        user="samyytids",
        password="Pokemon11",
        host="localhost"
    )

    encoding = tiktoken.encoding_for_model("text-embedding-3-large")
    test_query = encoding.encode("bright airy light natural modern cosy")
    # test_query = ["five", "bedrooms"]

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT feature FROM key_feature")
            features = cur.fetchall()
            features = np.array([encoding.encode(f[0]) for f in features], dtype=object)
            features = np.array([f for f in features], dtype=object)
            bm25 = BM25(features)
            scores = bm25.get_scores(test_query)
            sorted_indices = np.argsort(scores)[::-1]

            # Sort both arrays using the sorted indices
            sorted_data = features[sorted_indices]
            sorted_scores = scores[sorted_indices]
            for idx, score in enumerate(sorted_scores):
                # print(sorted_data[idx])
                print(encoding.decode(sorted_data[idx]))
                print(score)
                if idx == 10:
                    break

    e = time()
    print(e-s)