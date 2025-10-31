"""
Data loading and preprocessing module.

Lit les CSV publics hébergés sur Hugging Face (hardcodés),
et retombe en local (data/raw) si jamais l'URL échoue.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import pandas as pd

_HF_BASE = "https://huggingface.co/datasets/MehdiiAH/mangetamain/resolve/main/"
RECIPES_URL = _HF_BASE + "RAW_recipes.csv"
INTERACTIONS_URL = _HF_BASE + "RAW_interactions.csv"
READ_FROM_URLS_FIRST = True

# ------------------ LOGGING identique à ton code ------------------
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


class DataLoader:
    """Charge les données Food.com depuis HF (hardcodé) puis fallback local si besoin."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        self.data_path = Path("data/raw") if data_path is None else data_path

    def load_recipes(self, file: str = "RAW_recipes.csv") -> pd.DataFrame:
        """Charge les recettes (URL HF en priorité, sinon local)."""
        if READ_FROM_URLS_FIRST:
            try:
                logger.info(f"Téléchargement recettes depuis URL: {RECIPES_URL}")
                # low_memory=False pour éviter les dtypes cassés sur gros CSV
                df = pd.read_csv(RECIPES_URL, low_memory=False)
                logger.info("Recettes chargées depuis Hugging Face ✅")
                return df
            except Exception:
                logger.exception(
                    "Lecture via URL des recettes a échoué, essai en local…"
                )
        # fallback local
        path = self.data_path / file
        df = pd.read_csv(path, low_memory=False)
        logger.info(f"Recettes chargées depuis {path} ✅")
        return df

    def load_interactions(self, file: str = "RAW_interactions.csv") -> pd.DataFrame:
        """Charge les interactions (URL HF en priorité, sinon local)."""
        if READ_FROM_URLS_FIRST:
            try:
                logger.info(
                    f"Téléchargement interactions depuis URL: {INTERACTIONS_URL}"
                )
                df = pd.read_csv(INTERACTIONS_URL, low_memory=False)
                logger.info("Interactions chargées depuis Hugging Face ✅")
                return df
            except Exception:
                logger.exception(
                    "Lecture via URL des interactions a échoué, essai en local…"
                )
        # fallback local
        path = self.data_path / file
        df = pd.read_csv(path, low_memory=False)
        logger.info(f"Interactions chargées depuis {path} ✅")
        return df
