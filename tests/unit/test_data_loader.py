"""Tests simples pour DataLoader (lecture depuis Hugging Face)."""

import pytest
from food_analysis.core.data_loader import DataLoader

# ---------------------------
# Tests "remote" via Hugging Face
# ---------------------------

def test_data_loader_init_custom_path_remote_agnostic(tmp_path) -> None:
    """DataLoader accepte un chemin custom mais va lire depuis l'URL (comportement actuel)."""
    loader = DataLoader(data_path=tmp_path)
    assert loader.data_path == tmp_path  # attribut conservé


@pytest.mark.internet
def test_load_recipes_success_remote() -> None:
    """Charge les recettes depuis Hugging Face et vérifie le schéma minimal."""
    loader = DataLoader()
    df = loader.load_recipes()
    # On valide la structure / contenu général, pas un nombre exact de lignes
    assert len(df) > 1000
    expected_cols = {"name", "id", "minutes", "contributor_id", "submitted",
                     "n_steps", "n_ingredients"}
    assert expected_cols.issubset(set(df.columns))


@pytest.mark.internet
def test_load_interactions_success_remote() -> None:
    """Charge les interactions depuis Hugging Face et vérifie le schéma minimal."""
    loader = DataLoader()
    df = loader.load_interactions()
    assert len(df) > 1000
    expected_cols = {"user_id", "recipe_id", "rating", "date"}
    assert expected_cols.issubset(set(df.columns))
