# tests/test_data_loader.py
from pathlib import Path

import pandas as pd
import pytest

from food_analysis.core.data_loader import DataLoader


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Crée un dossier temporaire pour les tests."""
    return tmp_path


def test_init_with_default_path() -> None:
    """Teste que le chemin par défaut est bien 'data/raw'."""
    loader = DataLoader()
    assert loader.data_path == Path("data/raw")


def test_init_with_custom_path(tmp_data_dir: Path) -> None:
    """Teste que le chemin personnalisé est bien pris en compte."""
    loader = DataLoader(data_path=tmp_data_dir)
    assert loader.data_path == tmp_data_dir


def test_load_recipes_file_exists(tmp_data_dir: Path) -> None:
    """Teste le chargement correct du fichier RAW_recipes.csv."""
    # Création d’un petit CSV temporaire
    csv_path = tmp_data_dir / "RAW_recipes.csv"
    df_expected = pd.DataFrame({"id": [1, 2], "name": ["Cake", "Salad"]})
    df_expected.to_csv(csv_path, index=False)

    loader = DataLoader(data_path=tmp_data_dir)
    df_loaded = loader.load_recipes()

    # Vérifie que le contenu est identique
    pd.testing.assert_frame_equal(df_loaded, df_expected)


def test_load_interactions_file_exists(tmp_data_dir: Path) -> None:
    """Teste le chargement correct du fichier RAW_interactions.csv."""
    csv_path = tmp_data_dir / "RAW_interactions.csv"
    df_expected = pd.DataFrame({"recipe_id": [1], "rating": [5]})
    df_expected.to_csv(csv_path, index=False)

    loader = DataLoader(data_path=tmp_data_dir)
    df_loaded = loader.load_interactions()

    pd.testing.assert_frame_equal(df_loaded, df_expected)


def test_load_recipes_file_not_found(tmp_data_dir: Path) -> None:
    """Teste que FileNotFoundError est levée si RAW_recipes.csv est absent."""
    loader = DataLoader(data_path=tmp_data_dir)
    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_recipes()
    assert "RAW_recipes.csv" in str(exc_info.value)


def test_load_interactions_file_not_found(tmp_data_dir: Path) -> None:
    """Teste que FileNotFoundError est levée si RAW_interactions.csv est absent."""
    loader = DataLoader(data_path=tmp_data_dir)
    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_interactions()
    assert "RAW_interactions.csv" in str(exc_info.value)
