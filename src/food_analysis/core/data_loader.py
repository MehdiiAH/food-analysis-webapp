"""
Data loading and preprocessing module.

Ce module doit gérer le chargement des données Food.com.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import pandas as pd

# Messages de log à différents niveaux
logging.debug("Ceci est un message de niveau DEBUG")
logging.info("Ceci est un message de niveau INFO")
logging.warning("Ceci est un message de niveau WARNING")
logging.error("Ceci est un message de niveau ERROR")
logging.critical("Ceci est un message de niveau CRITICAL")

# Création d'un logger pour ce module
logger = logging.getLogger(__name__)

# Définir le niveau de log sur INFO
logger.setLevel(logging.INFO)

# Création d'un handler permettant la rotation des logs, avec format compréhensible

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

# Éviter d'ajouter plusieurs handlers si le module est importé plusieurs fois
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class DataLoader:
    """Classe servant à charger les données de Food.com."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        """
        Initialise le loader.

        Args:
            data_path: Chemin vers le dossier des données (optionnel)
        """
        if data_path is None:
            data_path = Path("data/raw")
        self.data_path = data_path

    def load_recipes(self, file: str = "RAW_recipes.csv") -> pd.DataFrame:
        """
        Charge les recettes depuis un fichier CSV.

        Args:
            path (str): chemin vers le fichier CSV

        Returns:
            pd.DataFrame: DataFrame contenant les recettes

        Raises:
            FileNotFoundError si le fichier n'est pas trouvé au chemin spécifié.
            EmptyDataError si le fichier est vide.
        """
        path = self.data_path / file
        try:
            df = pd.read_csv(path)
            logger.info(f"Données chargées avec succès depuis {path}.")
        except FileNotFoundError:
            logger.error(
                f"Erreur : fichier non disponible au chemin {path} spéficié.",
                exc_info=True,
            )
        except pd.errors.EmptyDataError:
            logger.warning("Attention: le fichier est vide.")
        return df

    def load_interactions(self, file: str = "RAW_interactions.csv") -> pd.DataFrame:
        """
        Charge les interactions (avis) depuis un fichier CSV.

        Args:
            path (str): chemin vers le fichier CSV

        Returns:
            pd.DataFrame: DataFrame contenant les interactions

        Raises:
            FileNotFoundError si le fichier n'est pas trouvé au chemin spécifié.
            EmptyDataError si le fichier est vide.
        """
        path = self.data_path / file
        try:
            df = pd.read_csv(path)
            logger.info(f"Données chargées avec succès depuis {path}.")
        except FileNotFoundError:
            logger.error(
                f"Erreur : fichier non disponible au chemin {path} spéficié.",
                exc_info=True,
            )
        except pd.errors.EmptyDataError:
            logger.warning("Attention: le fichier est vide.")
        return df
