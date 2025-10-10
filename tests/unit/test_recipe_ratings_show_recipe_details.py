from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.food_analysis.pages import recipe_ratings


@pytest.fixture
def mock_dataframes():
    """Mock les DataFrames utilisés dans la page."""
    recipe_df = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Tarte aux pommes", "Soupe à l’oignon"],
            "description": ["Une tarte délicieuse", "Une soupe réconfortante"],
            "rating": [4.5, 3.8],
            "nb_reviews": [10, 5],
        }
    )
    reviews_df = pd.DataFrame(
        {
            "recipe_id": [1, 1],
            "review_text": ["Excellent", "Très bon"],
            "rating": [5, 4],
        }
    )
    return recipe_df, reviews_df


@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mock l'API Streamlit (st) pour les tests."""
    mock_st = MagicMock()

    # ✅ Fonction robuste pour st.columns()
    def mock_columns_handler(arg=None, *_, **__):
        if isinstance(arg, int):
            count = arg
        elif isinstance(arg, (list, tuple)):
            count = len(arg)
        else:
            count = 4  # valeur par défaut
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns_handler

    # Mock des autres fonctions Streamlit
    mock_st.markdown = MagicMock()
    mock_st.dataframe = MagicMock()
    mock_st.selectbox = MagicMock(return_value="Tarte aux pommes")
    mock_st.write = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.error = MagicMock()

    monkeypatch.setattr(recipe_ratings, "st", mock_st)
    return mock_st


def test_show_recipe_details_no_reviews(mock_dataframes, mock_streamlit):
    """Vérifie l'affichage des détails d'une recette sans avis."""
    recipe_df, interaction_df = mock_dataframes

    # Retirer les reviews de la recette id=2 → aucun avis
    interaction_df = interaction_df[interaction_df["recipe_id"] != 2].copy()

    # ✅ Forcer la présence de toutes les colonnes nécessaires
    for col in ["recipe_id", "user_id", "rating", "date", "review"]:
        if col not in interaction_df.columns:
            interaction_df[col] = pd.Series(dtype="object")

    recipe_id = 2
    recipe_name = recipe_df.loc[recipe_df["id"] == recipe_id, "name"].iloc[0]
    recipe_stats = pd.Series(
        {
            "weighted_rating": 4.5,
            "avg_rating": 4.0,
            "n_reviews": 0,
        }
    )

    # Appel avec la bonne signature
    recipe_ratings.show_recipe_details(
        recipe_id=recipe_id,
        recipe_name=recipe_name,
        recipe_stats=recipe_stats,
        recipe_df=recipe_df,
        interaction_df=interaction_df,
    )

    # Vérifie que le titre et l'avertissement sont bien affichés
    mock_streamlit.markdown.assert_any_call(f"### 🍳 {recipe_name}")
    mock_streamlit.warning.assert_called_with(
        "Aucun avis disponible pour cette recette."
    )
