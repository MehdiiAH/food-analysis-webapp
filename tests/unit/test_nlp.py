import math

import numpy as np
import pytest
from scipy.sparse import csr_matrix

# On suppose que nlp.py est à la racine du projet ou accessible via PYTHONPATH
from food_analysis.core.nlp import (
    count_query,
    count_words,
    create_vocabulary,
    knn_search,
    tf_idf_search,
)

# -----------------------
# Fixtures de petit corpus
# -----------------------


@pytest.fixture
def tokenized_docs():
    # Chaque "texte" est une liste de tokens (malgré l'annotation List[str] dans le module)
    # 3 documents, vocabulaire attendu: {salade, tomate, pomme, banane, fromage}
    return [
        ["salade", "tomate"],
        ["pomme", "banane"],
        ["salade", "fromage"],
    ]


@pytest.fixture
def vocabulary(tokenized_docs):
    return create_vocabulary(tokenized_docs)


@pytest.fixture
def recipe_counts(tokenized_docs, vocabulary):
    return count_words(tokenized_docs, vocabulary)


# -----------------------
# create_vocabulary
# -----------------------


def test_create_vocabulary_returns_dict(tokenized_docs):
    vocab = create_vocabulary(tokenized_docs)
    assert isinstance(vocab, dict)
    # l'ordre n'est pas garanti, on vérifie seulement le contenu et la surjection vers [0..n-1]
    words = set().union(*map(set, tokenized_docs))
    assert set(vocab.keys()) == words
    assert set(vocab.values()) == set(range(len(words)))


def test_create_vocabulary_handles_duplicates(tokenized_docs):
    # Ajoute des doublons : le vocabulaire ne doit pas changer
    docs_with_dupes = tokenized_docs + [["salade", "salade", "salade"]]
    vocab1 = create_vocabulary(tokenized_docs)
    vocab2 = create_vocabulary(docs_with_dupes)
    assert set(vocab1.keys()) == set(vocab2.keys())
    assert len(vocab1) == len(vocab2)


# -----------------------
# count_words
# -----------------------


def test_count_words_shape_and_type(tokenized_docs, vocabulary):
    X = count_words(tokenized_docs, vocabulary)
    assert isinstance(X, csr_matrix)
    assert X.shape == (len(tokenized_docs), len(vocabulary))


def test_count_words_counts_are_correct(tokenized_docs, vocabulary):
    X = count_words(tokenized_docs, vocabulary)
    # Vérifie quelques comptes connus en se servant du vocabulaire pour indexer
    v = vocabulary
    d0 = X.toarray()[0]
    d1 = X.toarray()[1]
    d2 = X.toarray()[2]

    assert d0[v["salade"]] == 1
    assert d0[v["tomate"]] == 1
    assert d0.sum() == 2

    assert d1[v["pomme"]] == 1
    assert d1[v["banane"]] == 1
    assert d1.sum() == 2

    assert d2[v["salade"]] == 1
    assert d2[v["fromage"]] == 1
    assert d2.sum() == 2


# -----------------------
# count_query
# -----------------------


def test_count_query_known_and_unknown_tokens(vocabulary):
    # "salade" existe, "ananas" n'existe pas
    q = count_query(["salade", "salade", "ananas"], vocabulary)
    assert isinstance(q, csr_matrix)
    assert q.shape == (1, len(vocabulary)) or q.shape == (
        len(vocabulary),
    )  # tolère format 1D -> CSR 1xN
    arr = q.toarray().ravel()
    assert arr[vocabulary["salade"]] == 2
    # "ananas" ignoré => ne doit pas lever d'erreur et ne doit pas créer de nouvelle colonne
    assert "ananas" not in vocabulary


def test_count_query_all_unknown_tokens_gives_zeros(vocabulary):
    q = count_query(["xyz", "zzz"], vocabulary)
    arr = q.toarray().ravel()
    assert np.all(arr == 0)


# -----------------------
# tf_idf_search
# -----------------------


def test_tf_idf_search_types_and_shapes(recipe_counts, vocabulary):
    # Query = un seul token présent dans le vocab
    q_counts = count_query(["salade"], vocabulary)
    tfidf_docs, tfidf_query = tf_idf_search(recipe_counts, q_counts)

    assert isinstance(tfidf_docs, csr_matrix)
    assert isinstance(tfidf_query, csr_matrix)
    assert tfidf_docs.shape == (recipe_counts.shape[0], recipe_counts.shape[1])
    assert tfidf_query.shape[1] == recipe_counts.shape[1]
    assert tfidf_query.shape[0] == 1


def test_tf_idf_search_zero_query_ok(recipe_counts, vocabulary):
    # Query sans terme du vocab => vecteur TF-IDF nul
    q_counts = count_query(["terme_inconnu"], vocabulary)
    tfidf_docs, tfidf_query = tf_idf_search(recipe_counts, q_counts)
    assert tfidf_query.nnz == 0  # aucun élément non nul


# -----------------------
# knn_search
# -----------------------


def test_knn_search_returns_expected_neighbors(
    tokenized_docs, vocabulary, recipe_counts
):
    # Query qui contient "salade" => plus proches devraient être d0 et d2 (ceux qui contiennent "salade")
    q_counts = count_query(["salade"], vocabulary)
    tfidf_docs, tfidf_query = tf_idf_search(recipe_counts, q_counts)

    distances, indices = knn_search(tfidf_docs, k=2, query_input=tfidf_query)

    assert distances.shape == (1, 2)
    assert indices.shape == (1, 2)
    nearest = set(indices[0].tolist())
    # Les 2 plus proches sont les documents 0 et 2 (dans n'importe quel ordre)
    assert nearest == {0, 2}
    # Les distances doivent être identiques (même contenu, même longueur)
    assert math.isclose(distances[0, 0], distances[0, 1], rel_tol=1e-6, abs_tol=1e-9)


def test_knn_search_identical_document_distance_zero(
    tokenized_docs, vocabulary, recipe_counts
):
    # Query = exactement le doc 1 => distance cosinus ~ 0 sur le premier voisin
    q_counts = count_query(["pomme", "banane"], vocabulary)
    tfidf_docs, tfidf_query = tf_idf_search(recipe_counts, q_counts)

    distances, indices = knn_search(tfidf_docs, k=1, query_input=tfidf_query)
    assert indices[0, 0] == 1
    assert distances[0, 0] <= 1e-9  # zéro numérique


def test_knn_search_k_greater_than_n_raises(recipe_counts):
    # k > n_samples doit lever une ValueError depuis scikit-learn
    with pytest.raises(ValueError):
        _ = knn_search(recipe_counts, k=999, query_input=recipe_counts[0])
