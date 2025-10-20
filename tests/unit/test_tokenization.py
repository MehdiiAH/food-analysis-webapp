from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from spacy.tokens import Doc

from food_analysis.utils.tokenization import (
    extract_text_from_df,
    extract_tokens_from_df,
    extract_tokens_from_doc,
    store_tokens_in_df,
)

# ============================================================
# extract_text_from_df
# ============================================================


def test_extract_text_from_df_basic():
    df = pd.DataFrame(
        {
            "name": ["Pizza", "Pasta"],
            "description": ["Delicious tomato dish", "Creamy carbonara"],
        }
    )
    result = extract_text_from_df(df)
    assert "full_text" in result.columns
    assert len(result) == 2
    assert all(isinstance(x, str) for x in result["full_text"])


def test_extract_text_from_df_with_missing_values():
    df = pd.DataFrame(
        {
            "name": ["Pizza", None],
            "description": [None, "Yummy"],
        }
    )
    result = extract_text_from_df(df)
    assert len(result) == 2  # both rows have at least one non-null field
    assert "Pizza" in result["full_text"].iloc[0]
    assert "Yummy" in result["full_text"].iloc[1]


def test_extract_text_from_df_missing_columns():
    df = pd.DataFrame({"title": ["Soup"]})
    with pytest.raises(KeyError):
        extract_text_from_df(df)


# ============================================================
# extract_tokens_from_df
# ============================================================


@patch("food_analysis.utils.tokenization.spacy.load")
def test_extract_tokens_from_df_returns_docs_and_stopwords(mock_spacy_load):
    mock_nlp = MagicMock()
    mock_doc = MagicMock(spec=Doc)
    mock_nlp.pipe.return_value = [mock_doc]
    mock_nlp.Defaults.stop_words = {"the", "a", "and"}
    mock_spacy_load.return_value = mock_nlp

    df = pd.DataFrame({"full_text": ["Tomato sauce"]})
    docs, stopwords = extract_tokens_from_df(df)

    assert list(docs) == [mock_doc]
    assert stopwords == {"the", "a", "and"}
    mock_spacy_load.assert_called_once_with("en_core_web_sm", disable=["ner"])


def test_extract_tokens_from_df_missing_column():
    df = pd.DataFrame({"text": ["No full_text here"]})
    with pytest.raises(KeyError):
        extract_tokens_from_df(df)


# ============================================================
# extract_tokens_from_doc
# ============================================================


def test_extract_tokens_from_doc_filters_stopwords_and_non_alpha():
    mock_token = MagicMock()
    mock_token.is_alpha = True
    mock_token.pos_ = "NOUN"
    mock_token.lemma_ = "Tomato"

    mock_token2 = MagicMock()
    mock_token2.is_alpha = False
    mock_token2.pos_ = "NOUN"
    mock_token2.lemma_ = "123"

    doc = [mock_token, mock_token2]
    stopwords = {"tomato"}
    result = extract_tokens_from_doc(doc, stopwords)

    assert result == []  # "Tomato" is a stopword, other token is not alpha


# ============================================================
# store_tokens_in_df
# ============================================================


def test_store_tokens_in_df_success():
    df = pd.DataFrame({"full_text": ["A tasty soup"]})
    mock_doc = MagicMock(spec=Doc)
    stopwords = set()

    # Patch extract_tokens_from_doc to return deterministic result
    with patch(
        "food_analysis.utils.tokenization.extract_tokens_from_doc",
        return_value=["soup"],
    ):
        result = store_tokens_in_df([mock_doc], stopwords, df)

    assert "tokens" in result.columns
    assert result["tokens"].iloc[0] == ["soup"]


def test_store_tokens_in_df_length_mismatch_raises():
    df = pd.DataFrame({"full_text": ["one", "two"]})
    mock_doc = MagicMock(spec=Doc)
    stopwords = set()

    with pytest.raises(RuntimeError):
        store_tokens_in_df([mock_doc], stopwords, df)  # 1 doc, 2 rows mismatch
