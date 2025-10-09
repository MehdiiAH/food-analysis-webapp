"""Tests simples pour DataLoader."""

from pathlib import Path
import pandas as pd
import pytest
from food_analysis.core.data_loader import DataLoader


def test_data_loader_init_default() -> None:
    """Test que DataLoader s'initialise avec le chemin par défaut."""
    # Act
    loader = DataLoader()
    
    # Assert
    assert loader.data_path == Path("data/raw")


def test_data_loader_init_custom_path() -> None:
    """Test que DataLoader s'initialise avec un chemin personnalisé."""
    # Arrange
    custom_path = Path("/custom/path")
    
    # Act
    loader = DataLoader(data_path=custom_path)
    
    # Assert
    assert loader.data_path == custom_path


def test_load_recipes_file_not_found() -> None:
    """Test que load_recipes lève FileNotFoundError si le fichier n'existe pas."""
    # Arrange
    loader = DataLoader(data_path=Path("/nonexistent"))
    
    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_recipes()
    
    assert "RAW_recipes.csv" in str(exc_info.value)


def test_load_recipes_success(tmp_path: Path) -> None:
    """Test que load_recipes charge correctement un fichier CSV."""
    # Arrange : Créer un fichier CSV temporaire
    csv_content = "id,name,minutes\n1,Recipe A,30\n2,Recipe B,45\n"
    csv_file = tmp_path / "RAW_recipes.csv"
    csv_file.write_text(csv_content)
    
    loader = DataLoader(data_path=tmp_path)
    
    # Act
    df = loader.load_recipes()
    
    # Assert
    assert len(df) == 2
    assert "id" in df.columns
    assert "name" in df.columns
    assert df.iloc[0]["name"] == "Recipe A"


def test_load_interactions_file_not_found() -> None:
    """Test que load_interactions lève FileNotFoundError si le fichier n'existe pas."""
    # Arrange
    loader = DataLoader(data_path=Path("/nonexistent"))
    
    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_interactions()
    
    assert "RAW_interactions.csv" in str(exc_info.value)


def test_load_interactions_success(tmp_path: Path) -> None:
    """Test que load_interactions charge correctement un fichier CSV."""
    # Arrange
    csv_content = "user_id,recipe_id,rating\n101,1,5\n102,2,4\n"
    csv_file = tmp_path / "RAW_interactions.csv"
    csv_file.write_text(csv_content)
    
    loader = DataLoader(data_path=tmp_path)
    
    # Act
    df = loader.load_interactions()
    
    # Assert
    assert len(df) == 2
    assert "user_id" in df.columns
    assert "rating" in df.columns
    assert df.iloc[0]["rating"] == 5