# tests/test_recipe_ratings_page.py
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from food_analysis.pages.recipe_ratings_page import (
    show_recipe_details,
    show_recipe_ratings_page,
)


@pytest.fixture
def sample_data() -> None:
    recipe_df = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Pasta", "Pizza"],
            "minutes": [30, 75],
        }
    )
    interaction_df = pd.DataFrame(
        {
            "recipe_id": [1, 1, 2, 2],
            "rating": [5, 4, 3, 0],
            "review": ["Excellent", "Good", "Ok", ""],
            "date": ["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01"],
        }
    )
    return recipe_df, interaction_df


@patch("food_analysis.pages.recipe_ratings_page.st", autospec=True)
@patch("food_analysis.pages.recipe_ratings_page.compute_recipe_stats")
def test_show_recipe_ratings_page_runs(
    mock_compute_stats, mock_st, sample_data
) -> None:
    recipe_df, interaction_df = sample_data

    # Mock le résultat de compute_recipe_stats
    mock_compute_stats.return_value = pd.DataFrame(
        {
            "name": ["Pasta", "Pizza"],
            "avg_rating": [4.5, 3.0],
            "weighted_rating": [4.4, 2.8],
            "n_reviews": [20, 10],
        }
    )

    # Mock des composants Streamlit
    mock_st.slider.side_effect = [10, 2]  # m et n_recipes
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    mock_st.dataframe.return_value = MagicMock(selection=MagicMock(rows=[0]))

    # Exécute la fonction
    show_recipe_ratings_page(recipe_df, interaction_df)

    # ✅ Vérifie que compute_recipe_stats a été appelé
    mock_compute_stats.assert_called_once_with(recipe_df, interaction_df, m=10)

    # ✅ Vérifie que le header et le tableau ont été affichés
    mock_st.header.assert_called_with("🏆 Recettes les Mieux Notées")
    mock_st.dataframe.assert_called()


@patch("food_analysis.pages.recipe_ratings_page.st", autospec=True)
@patch("food_analysis.pages.recipe_ratings_page.recipe_reviews")
def test_show_recipe_details(mock_reviews, mock_st, sample_data) -> None:
    recipe_df, interaction_df = sample_data

    recipe_stats = pd.Series(
        {"weighted_rating": 4.5, "avg_rating": 4.0, "n_reviews": 15}
    )

    # Mock les avis
    mock_reviews.return_value = pd.DataFrame(
        {
            "rating": [5, 4, 0],
            "review": ["Excellent", "Good", ""],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        }
    )

    # Mock des fonctions Streamlit utilisées
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    mock_st.metric.return_value = None
    mock_st.multiselect.return_value = [5, 4, 0]
    mock_st.number_input.return_value = 2
    mock_st.expander.return_value.__enter__.return_value = MagicMock()
    mock_st.container.return_value.__enter__.return_value = MagicMock()

    # Exécution
    show_recipe_details(
        recipe_id=1,
        recipe_name="Pasta",
        recipe_stats=recipe_stats,
        recipe_df=recipe_df,
        interaction_df=interaction_df,
    )

    # ✅ Vérifie que recipe_reviews a été appelé
    mock_reviews.assert_called_once_with(1, interaction_df)

    # ✅ Vérifie qu’au moins une métrique est affichée
    assert mock_st.metric.call_count >= 3
