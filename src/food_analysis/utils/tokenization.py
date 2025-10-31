"""
The module contains functions to tokenize the recipe dataframe
"""

import logging
import subprocess
from logging.handlers import RotatingFileHandler
from typing import Iterable, List, Set, Tuple

import pandas as pd
import spacy
from spacy.tokens import Doc

# ----------------------
# Logging
# ----------------------
logging.debug("Ceci est un message de niveau DEBUG")
logging.info("Ceci est un message de niveau INFO")
logging.warning("Ceci est un message de niveau WARNING")
logging.error("Ceci est un message de niveau ERROR")
logging.critical("Ceci est un message de niveau CRITICAL")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "tokenization.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
handler_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(handler_format)

console_handler = logging.StreamHandler()
console_handler.setFormatter(handler_format)
console_handler.setLevel(logging.INFO)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ----------------------
# SpaCy Model Loader
# ----------------------
def load_spacy_model():
    """
    Charge le modèle SpaCy 'en_core_web_sm'.
    Si le modèle n'est pas installé, il sera téléchargé automatiquement.
    """
    try:
        return spacy.load("en_core_web_sm", disable=["ner"])
    except OSError:
        logger.info("Modèle en_core_web_sm manquant, téléchargement en cours...")
        subprocess.run(
            ["python", "-m", "spacy", "download", "en_core_web_sm"], check=True
        )
        return spacy.load("en_core_web_sm", disable=["ner"])


# Charger une seule fois le modèle
nlp_model = load_spacy_model()


# ----------------------
# Fonctions principales
# ----------------------
def extract_text_from_df(df: pd.DataFrame) -> pd.DataFrame:
    test_columns = ["name", "description"]
    missing_columns = [col for col in test_columns if col not in df.columns]
    if len(missing_columns) == len(test_columns):
        logger.error("Columns 'name' and 'description' are missing")
        raise KeyError("name, description")
    if len(missing_columns) > 0:
        logger.warning(
            "Missing columns in the dataframe. Unexpected results may be found"
        )
    else:
        logger.info("Dataframe is correctly built")

    mask = df[["name", "description"]].notna().any(axis=1)
    data_text = df.loc[mask, ["name", "description"]].copy()
    data_text["full_text"] = (
        data_text["name"].fillna("") + " " + data_text["description"].fillna("")
    )
    logger.info("Name and description extracted from dataframe")
    return data_text


def extract_tokens_from_df(df: pd.DataFrame) -> Tuple[Iterable[Doc], Set[str]]:
    stopwords = {w.lower() for w in nlp_model.Defaults.stop_words}

    try:
        df["full_text"]
    except KeyError:
        logger.error("No column existing for tokenization")

    texts = df["full_text"].tolist()
    docs = nlp_model.pipe(texts, batch_size=50, n_process=4)
    logger.info("Tokenization complete")

    return docs, stopwords


def extract_tokens_from_doc(doc: Doc, stopwords: Set[str]) -> List[str]:
    return [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha
        and token.pos_ in {"NOUN", "ADJ"}
        and token.lemma_.lower() not in stopwords
    ]


def store_tokens_in_df(
    docs: Iterable[Doc], stopwords: Set[str], df: pd.DataFrame
) -> pd.DataFrame:
    tokens_extracted = [extract_tokens_from_doc(doc, stopwords) for doc in docs]
    logger.info("Tokens extracted")

    if len(tokens_extracted) != len(df):
        raise RuntimeError("Mismatch between number of documents and dataframe size")

    if "tokens" not in df.columns:
        df["tokens"] = pd.Series([None] * len(df), index=df.index, dtype=object)
    else:
        df["tokens"] = df["tokens"].astype(object)

    tokens_series = pd.Series(tokens_extracted, index=df.index, dtype=object)
    df.loc[df.index, "tokens"] = tokens_series
    logger.info("Tokens stored in dataframe")
    return df


def extract_tokens_from_string(query_text: str) -> List[str]:
    if not query_text:
        logger.error("User has indicated an empty string for the search")
        raise ValueError("Searched string empty")

    stopwords = {w.lower() for w in nlp_model.Defaults.stop_words}
    docs = list(nlp_model.pipe([query_text]))
    query_doc = docs[0]
    tokens_extracted = extract_tokens_from_doc(query_doc, stopwords)
    logger.info("User search tokenized")
    return tokens_extracted
