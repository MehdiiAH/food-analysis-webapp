from pathlib import Path
import pandas as pd


class DataLoader:
    """Charge les données Food.com."""

    def __init__(self, data_path: Path = None) -> None:
        """Initialise le loader."""
        if data_path is None:
            data_path = Path("data/raw")
        self.data_path = data_path

    def load_recipes(self) -> pd.DataFrame:
        """Charge les recettes."""
        file_path = self.data_path / "RAW_recipes.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé : {file_path}")
        return pd.read_csv(file_path)

    def load_interactions(self) -> pd.DataFrame:
        """Charge les interactions."""
        file_path = self.data_path / "RAW_interactions.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé : {file_path}")
        return pd.read_csv(file_path)