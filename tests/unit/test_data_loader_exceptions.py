import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import pandas as pd

# Création d’un logger pour ce module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler de fichier rotatif
file_handler = RotatingFileHandler(
    "data_loader.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Évite la duplication de handlers
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class DataLoader:
    """Classe servant à charger les données de Food.com."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        if data_path is None:
            data_path = Path("data/raw")
        self.data_path = data_path

    def load_recipes(self, file: str = "RAW_recipes.csv") -> pd.DataFrame:
        """Charge les recettes depuis un fichier CSV."""
        path = self.data_path / file
        try:
            df = pd.read_csv(path)
            logger.info(f"Données chargées avec succès depuis {path}.")
        except FileNotFoundError:
            logger.error(
                f"Erreur : fichier non disponible au chemin {path} spécifié.",
                exc_info=True,
            )
            df = pd.DataFrame()  # ✅ Définit un DataFrame vide
        except pd.errors.EmptyDataError:
            logger.warning("Attention: le fichier est vide.")
            df = pd.DataFrame()  # ✅ Définit un DataFrame vide
        return df

    def load_interactions(self, file: str = "RAW_interactions.csv") -> pd.DataFrame:
        """Charge les interactions (avis) depuis un fichier CSV."""
        path = self.data_path / file
        try:
            df = pd.read_csv(path)
            logger.info(f"Données chargées avec succès depuis {path}.")
        except FileNotFoundError:
            logger.error(
                f"Erreur : fichier non disponible au chemin {path} spécifié.",
                exc_info=True,
            )
            df = pd.DataFrame()
        except pd.errors.EmptyDataError:
            logger.warning("Attention: le fichier est vide.")
            df = pd.DataFrame()
        return df
