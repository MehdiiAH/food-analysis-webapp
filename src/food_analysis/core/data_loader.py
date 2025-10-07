from pathlib import Path
from typing import Optional

import pandas as pd


class DataLoader:
    """Charge les données Food.com."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        """
        Initialise le loader.

        Args:
            data_path: Chemin vers le dossier des données (optionnel)
        """
        if data_path is None:
            data_path = Path("data/raw")
        self.data_path = data_path

    def load_recipes(self) -> pd.DataFrame:
        """
        Charge les recettes.

        Returns:
            DataFrame contenant les recettes

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
        """
        file_path = self.data_path / "RAW_recipes.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé : {file_path}")
        return pd.read_csv(file_path)

    def load_interactions(self) -> pd.DataFrame:
        """
        Charge les interactions.

        Returns:
            DataFrame contenant les interactions

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
        """
        file_path = self.data_path / "RAW_interactions.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé : {file_path}")
        return pd.read_csv(file_path)
