"""
DataLoader — optimisé (RAM) et compatible mypy
- Lecture depuis Hugging Face (URLs publiques)
- Cache parquet en /tmp
- Colonnes et dtypes réduits
- Colonne `review` incluse
"""

from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd
import requests  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === URLs Hugging Face (constantes) ===
_HF_BASE: str = "https://huggingface.co/datasets/MehdiiAH/mangetamain/resolve/main/"
RECIPES_URL: str = f"{_HF_BASE}RAW_recipes.csv"
INTERACTIONS_URL: str = f"{_HF_BASE}RAW_interactions.csv"

# === Colonnes / dtypes (RAM-friendly) ===
RECIPES_USECOLS: list[str] = [
    "name",
    "id",
    "minutes",
    "contributor_id",
    "submitted",
    "tags",
    "nutrition",
    "n_steps",
    "steps",
    "description",
    "ingredients",
    "n_ingredients",
]
RECIPES_DTYPES: dict[str, str] = {
    "name": "string",
    "id": "int32",
    "minutes": "int32",
    "contributor_id": "int32",
    "tags": "string",
    "nutrition": "string",
    "n_steps": "int16",
    "steps": "string",
    "description": "string",
    "ingredients": "string",
    "n_ingredients": "int16",
}

# IMPORTANT: review incluse
INTER_USECOLS: list[str] = ["user_id", "recipe_id", "rating", "date", "review"]
INTER_DTYPES: dict[str, str] = {
    "user_id": "int64",
    "recipe_id": "int32",
    "rating": "int8",
    "review": "string",
}


class DataLoader:
    """Gestion centralisée du chargement des datasets."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        # Dossier cache (parquet) — /tmp par défaut, compatible Streamlit Cloud
        base: str = data_path if data_path is not None else tempfile.gettempdir()
        self._cache_dir: Path = Path(base) / "food_cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------ utilitaires cache ------------------

    def _cache_path(self, stem: str) -> Path:
        """Chemin du fichier parquet de cache."""
        return self._cache_dir / f"{stem}.parquet"

    def _load_parquet(self, stem: str) -> Optional[pd.DataFrame]:
        path = self._cache_path(stem)
        if path.exists():
            try:
                df = pd.read_parquet(path)
                logger.info("✅ Chargé depuis cache : %s", path)
                return df
            except Exception as e:  # pragma: no cover — robustesse
                logger.warning("Cache corrompu (%s), suppression. Raison: %s", path, e)
                try:
                    path.unlink()
                except Exception:
                    pass
        return None

    def _save_parquet(self, stem: str, df: pd.DataFrame) -> None:
        path = self._cache_path(stem)
        try:
            df.to_parquet(path, index=False)
            logger.info("💾 Cache enregistré : %s", path)
        except Exception as e:  # pragma: no cover — non bloquant
            logger.warning("Impossible d'écrire le cache (%s): %s", path, e)

    # ------------------ téléchargements ------------------

    @staticmethod
    def _http_get_bytes(url: str, timeout: int) -> bytes:
        """Télécharge une ressource et renvoie son contenu binaire (pour BytesIO)."""
        resp = requests.get(url, timeout=timeout)  # type: ignore[no-untyped-call]
        resp.raise_for_status()
        return resp.content

    # ------------------ API publique ------------------

    def load_recipes(self) -> pd.DataFrame:
        """Charge les recettes (HF → cache parquet)."""
        cache_stem = "RAW_recipes"
        cached = self._load_parquet(cache_stem)
        if cached is not None:
            return cached

        logger.info("Téléchargement recettes depuis URL: %s", RECIPES_URL)
        data: bytes = self._http_get_bytes(RECIPES_URL, timeout=60)

        df = pd.read_csv(
            io.BytesIO(data),
            usecols=RECIPES_USECOLS,
            dtype=RECIPES_DTYPES,
            parse_dates=["submitted"],
            infer_datetime_format=True,
            low_memory=True,
        )
        logger.info("Recettes chargées depuis Hugging Face ✅")

        self._save_parquet(cache_stem, df)
        return df

    def load_interactions(self) -> pd.DataFrame:
        """Charge les interactions (HF → cache parquet)."""
        cache_stem = "RAW_interactions"
        cached = self._load_parquet(cache_stem)
        if cached is not None:
            return cached

        logger.info("Téléchargement interactions depuis URL: %s", INTERACTIONS_URL)
        data: bytes = self._http_get_bytes(INTERACTIONS_URL, timeout=90)

        df = pd.read_csv(
            io.BytesIO(data),
            usecols=INTER_USECOLS,
            dtype=INTER_DTYPES,
            parse_dates=["date"],
            infer_datetime_format=True,
            low_memory=True,
        )
        df["review"] = df["review"].astype("string").str.slice(0, 800)

        logger.info("Interactions chargées depuis Hugging Face ✅")

        self._save_parquet(cache_stem, df)
        return df
