"""
The module contains functions to execute a search based on NLP using TF-IDF
(Term Frequency-Inverse Document Frequency) and nearest neighbours algorithms
"""

import json
from typing import Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix, save_npz
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

    save_vocabulary_counts(counts_sparse, vocabulary)

    return counts_sparse


def count_query(tokens: List[str], vocabulary: Dict) -> csr_matrix:
    """
    The function creates a bag of words from a list of document
    and a vocabulary in a sparse format

    Parameters:
    -----------
    tokens: List[str]
        A list of tokens created with a tokenizer
        from the user searched string
    vocabulary: Dict
        The dictionary of words to be counted

    Returns:
    --------
    counts_sparse: csr_matrix
        A sparse matrix containing the number of each word
        in each document.

    """
    count_vector = np.zeros(len(vocabulary), dtype=int)

    # Filling the matrix by iterating over the documents and counting the words
    for word in tokens:
        if word in vocabulary:
            count_vector[vocabulary[word]] += 1

    # Creating a sparse matrix for TF-IDF transformation
    counts_sparse = csr_matrix(count_vector)

    return counts_sparse


def tf_idf_search(
    recipe_counts: csr_matrix,
    query_counts: csr_matrix,
) -> Tuple[csr_matrix, csr_matrix]:
    """
    The function converts a bag of words in TF-IDF matrix for
    the reference dataset and for the searched string

    Parameters:
    -----------
    recipe_counts: csr_matrix
        A sparse matrix containing the BoW
    quey_counts: csr_matrix
        A sparse matrix containing the tokenized query as a BoW

    Returns:
    --------
    tf_idf_recipe: csr_matrix
        A sparse matrix transformed in TF-IDF for the dataset
    tf_idf_query: csr_matrix
        A sparse matrix transformed in TF-IDF for the query
    """
    transformer = TfidfTransformer()
    tf_idf_recipe = transformer.fit_transform(recipe_counts)
    tf_idf_query = transformer.transform(query_counts)

    # Ensure we always return a CSR sparse matrix (fit_transform may return ndarray)
    if isinstance(tf_idf_recipe, csr_matrix):
        if isinstance(tf_idf_query, csr_matrix):
            return tf_idf_recipe, tf_idf_query
        else:
            return tf_idf_recipe, csr_matrix(tf_idf_query)
    else:
        if isinstance(tf_idf_query, csr_matrix):
            return csr_matrix(tf_idf_recipe), tf_idf_query
        else:
            return csr_matrix(tf_idf_recipe), csr_matrix(tf_idf_query)


def knn_search(
    tf_idf: csr_matrix, k: int, query_input: csr_matrix
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The function trains a KNN model on the TF-IDF matrix
    and search for the nearest neighbors of the searched string

    Parameters:
    -----------
    tf_idf: csr_matrix
        A sparse matrix containing the result of the TF-IDF
    k: int
        The number of neighbors
    query_input: csr_matrix
        A vector transformed by the same TF-IDF

    Returns:
    --------
    distances: np.ndarray
        An array of distances
    indices: np.ndarray
        An array with the indices of the nearest recipes

    """
    knn_model = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
    knn_model.fit(tf_idf)
    distances, indices = knn_model.kneighbors(query_input)

    return distances, indices


def save_vocabulary_counts(matrix: csr_matrix, vocabulary: Dict) -> None:
    """
    The function saves the dictionary and the bag of words for further use

    Parameters:
    -----------
    matrix: csr_matrix
        A sparse matrix containing the bag of word
    vocabulary: Dict
        A dictionary containing the vocabulary
    """
    save_npz("data/processed/matrix.npz", matrix)

    with open("data/processed/dict.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary, f)

    return None
