# src/food_analysis/core/data_loader.py
"""
Data loading and preprocessing module.

- Lit les CSV publics hébergés sur Hugging Face (URLs hardcodées).
- Réduit l'empreinte mémoire (usecols + dtypes downcast).
- Met en cache en Parquet dans /tmp pour éviter de reparser à chaque run.
- Compatible mypy (annotations, pandas typing).
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Literal, Optional, cast

import pandas as pd
from pandas._typing import DtypeArg

# ------------------ CONFIG URLs (hardcodées) ------------------
_HF_BASE = "https://huggingface.co/datasets/MehdiiAH/mangetamain/resolve/main/"
RECIPES_URL: str = _HF_BASE + "RAW_recipes.csv"
INTERACTIONS_URL: str = _HF_BASE + "RAW_interactions.csv"
READ_FROM_URLS_FIRST: bool = True

# ------------------ Parquet cache local ------------------
PARQUET_DIR: Path = Path("/tmp/food_cache")
RECIPES_PARQUET: Path = PARQUET_DIR / "recipes.parquet"
INTER_PARQUET: Path = PARQUET_DIR / "interactions.parquet"

PARQUET_ENGINE: Literal["auto", "pyarrow", "fastparquet"] = "pyarrow"

# ------------------ Colonnes minimales + dtypes downcast ------------------
RECIPES_USECOLS: List[str] = [
    "id",
    "name",
    "minutes",
    "contributor_id",
    "submitted",
    "n_steps",
    "n_ingredients",
]
RECIPES_DTYPES: Dict[str, DtypeArg] = {
    "id": "int32",
    "minutes": "int32",  # int16 peut overflow si valeurs extrêmes
    "contributor_id": "int32",
    "n_steps": "int16",
    "n_ingredients": "int8",
    # "name": string (appliqué après), "submitted": datetime
}

INTER_USECOLS: List[str] = ["user_id", "recipe_id", "rating", "date"]
INTER_DTYPES: Dict[str, DtypeArg] = {
    "user_id": "int64",
    "recipe_id": "int32",
    "rating": "int8",
    # "date": datetime
}

# ------------------ LOGGING identique ------------------
logging.debug("Ceci est un message de niveau DEBUG")
logging.info("Ceci est un message de niveau INFO")
logging.warning("Ceci est un message de niveau WARNING")
logging.error("Ceci est un message de niveau ERROR")
logging.critical("Ceci est un message de niveau CRITICAL")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "data_loader.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
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


def _ensure_parquet_dir() -> None:
    """Crée le dossier cache parquet si besoin."""
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)


def _read_recipes_from_url() -> pd.DataFrame:
    """Lit les recettes depuis l'URL HF (CSV) avec options RAM-friendly."""
    logger.info(f"Téléchargement recettes depuis URL: {RECIPES_URL}")
    df: pd.DataFrame = pd.read_csv(
        RECIPES_URL,
        usecols=RECIPES_USECOLS,
        dtype=RECIPES_DTYPES,
        parse_dates=["submitted"],
        date_format="mixed",
        low_memory=True,
    )
    # string dtype moderne (compact + évite object)
    df["name"] = df["name"].astype("string")
    return df


def _read_interactions_from_url() -> pd.DataFrame:
    """Lit les interactions depuis l'URL HF (CSV) avec options RAM-friendly."""
    logger.info(f"Téléchargement interactions depuis URL: {INTERACTIONS_URL}")
    df: pd.DataFrame = pd.read_csv(
        INTERACTIONS_URL,
        usecols=INTER_USECOLS,
        dtype=INTER_DTYPES,
        parse_dates=["date"],
        date_format="mixed",
        low_memory=True,
    )
    return df


class DataLoader:
    """Charge les données Food.com depuis HF (hardcodé) + cache parquet local /tmp, sinon fallback local."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        self.data_path: Path = Path("data/raw") if data_path is None else data_path
        _ensure_parquet_dir()

    # --- API publique ---
    def load_recipes(self, file: str = "RAW_recipes.csv") -> pd.DataFrame:
        """Charge le DataFrame des recettes (parquet cache -> URL HF -> local)."""
        # 1) Parquet local si dispo (évite reparse CSV)
        if RECIPES_PARQUET.exists():
            try:
                df = cast(
                    pd.DataFrame,
                    pd.read_parquet(path=RECIPES_PARQUET, engine=PARQUET_ENGINE),
                )
                return df
            except Exception:
                logger.exception(
                    "Lecture Parquet recipes échouée, on retente via URL/local…"
                )

        # 2) URL HF
        if READ_FROM_URLS_FIRST:
            try:
                df = _read_recipes_from_url()
                try:
                    df.to_parquet(
                        path=RECIPES_PARQUET, engine=PARQUET_ENGINE, index=False
                    )
                except Exception:
                    logger.warning(
                        "Impossible d'écrire le cache Parquet recipes (non bloquant)."
                    )
                logger.info("Recettes chargées depuis Hugging Face ✅")
                return df
            except Exception:
                logger.exception(
                    "Lecture via URL des recettes a échoué, essai en local…"
                )

        # 3) Fallback local minimal
        path = self.data_path / file
        df_local: pd.DataFrame = pd.read_csv(
            path,
            usecols=RECIPES_USECOLS,
            dtype=RECIPES_DTYPES,
            parse_dates=["submitted"],
            date_format="mixed",
            low_memory=True,
        )
        logger.info(f"Recettes chargées depuis {path} ✅")
        return df_local

    def load_interactions(self, file: str = "RAW_interactions.csv") -> pd.DataFrame:
        """Charge le DataFrame des interactions (parquet cache -> URL HF -> local)."""
        if INTER_PARQUET.exists():
            try:
                df = cast(
                    pd.DataFrame,
                    pd.read_parquet(path=INTER_PARQUET, engine=PARQUET_ENGINE),
                )
                return df
            except Exception:
                logger.exception(
                    "Lecture Parquet interactions échouée, on retente via URL/local…"
                )

        if READ_FROM_URLS_FIRST:
            try:
                df = _read_interactions_from_url()
                try:
                    df.to_parquet(
                        path=INTER_PARQUET, engine=PARQUET_ENGINE, index=False
                    )
                except Exception:
                    logger.warning(
                        "Impossible d'écrire le cache Parquet interactions (non bloquant)."
                    )
                logger.info("Interactions chargées depuis Hugging Face ✅")
                return df
            except Exception:
                logger.exception(
                    "Lecture via URL des interactions a échoué, essai en local…"
                )

        path = self.data_path / file
        df_local: pd.DataFrame = pd.read_csv(
            path,
            usecols=INTER_USECOLS,
            dtype=INTER_DTYPES,
            parse_dates=["date"],
            date_format="mixed",
            low_memory=True,
        )
        logger.info(f"Interactions chargées depuis {path} ✅")
        return df_local
