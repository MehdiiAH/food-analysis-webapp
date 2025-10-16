"""
The module contains functions to execute a search based on NLP using TF-IDF
(Term Frequency-Inverse Document Frequency) and nearest neighbours algorithms
"""

from typing import Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import NearestNeighbors


def create_vocabulary(texts: List[str]) -> Dict:
    """
    The function reads the tokens extracted to build
    a vocabulary dictionary of each word

    Parameters:
    -----------
    texts: List[str]
        A list of texts created with a tokenizer

    Returns:
    --------
    vocabulary: Dict
        The dictionary of words to be counted

    """
    words: set[str] = set()
    for t in texts:
        words = words.union(set(t))
    n_features = len(words)
    vocabulary = dict(zip(words, range(n_features)))

    return vocabulary


def count_words(texts: List[str], vocabulary: Dict) -> csr_matrix:
    """
    The function creates a bag of words from a list of document
    and a vocabulary in a sparse format

    Parameters:
    -----------
    texts: List[str]
        A list of texts created with a tokenizer
    vocabulary: Dict
        The dictionary of words to be counted

    Returns:
    --------
    counts_sparse: csr_matrix
        A sparse matrix containing the number of each word
        in each document.

    """
    n_samples = len(texts)
    n_features = len(vocabulary)

    counts = np.zeros((n_samples, n_features))

    # Filling the matrix by iterating over the documents and counting the words
    for k, t in enumerate(texts):
        for w in t:
            counts[k][vocabulary[w]] += 1.0

    # Creating a sparse matrix for TF-IDF transformation
    counts_sparse = csr_matrix(counts)

    return counts_sparse


def tf_idf_transformer() -> TfidfTransformer:
    """
    Set a TF-IDF transformer from library Scikit-Learn

    Returns
    -------
    transformer : TfidfTransformer
        A transformer ready to apply on a BoW
    """
    transformer = TfidfTransformer()

    return transformer


def tf_idf_recipes(counts: csr_matrix, transformer: TfidfTransformer) -> csr_matrix:
    """
    The function converts a bag of words in TF-IDF matrix

    Parameters:
    -----------
    counts: csr_matrix
        A sparse matrix containing the BoW
    transformer: TfidfTransformer
        The transformer for the TF-IDF

    Returns:
    --------
    tf_idf: csr_matrix
        A sparse matrix transformed in TF-IDF
    """
    tf_idf = transformer.fit_transform(counts)

    # Ensure we always return a CSR sparse matrix (fit_transform may return ndarray)
    if isinstance(tf_idf, csr_matrix):
        return tf_idf
    return csr_matrix(tf_idf)


def knn_train(tf_idf: csr_matrix, k: int) -> NearestNeighbors:
    """
    The function trains a KNN model on the TF-IDF matrix

    Parameters:
    -----------
    tf_idf: csr_matrix
        A sparse matrix containing the result of the TF-IDF
    k: int
        The number of neighbors

    Returns:
    --------
    knn_model: NearestNeighbors
        The model trained on the TF-IDF
    """
    knn_model = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")

    knn_model.fit(tf_idf)

    return knn_model


def knn_search(
    knn_model: NearestNeighbors, query_input: csr_matrix
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The function sends back the nearest neighbors of the user search with distances

    Parameters:
    -----------
    knn_model: NearestNeighbors
        A knn model trained on the recipe dataset with TF-IDF
    query_input: csr_matrix
        A vector transformed by the same TF-IDF

    Returns:
    distances: np.ndarray
        An array of distances
    indices: np.ndarray
        An array with the indices of the nearest recipes
    """
    distances, indices = knn_model.kneighbors(query_input)
    return distances, indices
