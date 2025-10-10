import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.insert(0, "src")
from food_analysis.pages import recipe_ratings


@pytest.fixture
def recipe_df():
    return pd.DataFrame({"id": [1, 2, 3], "name": ["Pizza", "Burger", "Salade"]})


@pytest.fixture
def interaction_df():
    return pd.DataFrame(
        {
            "recipe_id": [1, 1, 2, 3, 3],
            "user_id": [10, 11, 12, 13, 14],
            "rating": [5, 4, 3, 5, 4],
            "date": pd.date_range("2024-01-01", periods=5),
            "review": ["bon", "excellent", "ok", "top", "super"],
        }
    )


@pytest.fixture
def recipe_stats_df(recipe_df):
    # Ce DataFrame simulera la sortie de compute_recipe_stats
    return pd.DataFrame(
        {
            "name": ["Pizza", "Burger", "Salade"],
            "weighted_rating": [4.8, 4.2, 3.9],
            "avg_rating": [4.5, 4.0, 3.7],
            "n_reviews": [100, 50, 10],
        }
    )


@patch("food_analysis.pages.recipe_ratings.show_recipe_details")
@patch("food_analysis.pages.recipe_ratings.compute_recipe_stats")
def test_show_recipe_ratings_page_basic(
    mock_compute, mock_show_details, recipe_df, interaction_df, recipe_stats_df
):
    mock_compute.return_value = recipe_stats_df

    # Patch streamlit functions pour éviter l'affichage réel
    with patch("food_analysis.pages.recipe_ratings.st") as mock_st:
        mock_st.slider.return_value = 10
        mock_st.dataframe.return_value.selection.rows = [0]
        mock_st.columns.return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        mock_st.spinner.__enter__.return_value = None
        mock_st.spinner.__exit__.return_value = None

        recipe_ratings.show_recipe_ratings_page(recipe_df, interaction_df)

        mock_compute.assert_called_once()
        mock_show_details.assert_called_once()


@patch("food_analysis.pages.recipe_ratings.show_recipe_details")
@patch("food_analysis.pages.recipe_ratings.compute_recipe_stats")
def test_show_recipe_ratings_page_no_selection(
    mock_compute, mock_show_details, recipe_df, interaction_df, recipe_stats_df
):
    mock_compute.return_value = recipe_stats_df

    with patch("food_analysis.pages.recipe_ratings.st") as mock_st:
        mock_st.slider.return_value = 10
        mock_st.dataframe.return_value.selection.rows = []
        mock_st.columns.return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        mock_st.spinner.__enter__.return_value = None
        mock_st.spinner.__exit__.return_value = None

        recipe_ratings.show_recipe_ratings_page(recipe_df, interaction_df)

        mock_show_details.assert_called_once()


@patch("food_analysis.pages.recipe_ratings.show_recipe_details")
@patch("food_analysis.pages.recipe_ratings.compute_recipe_stats")
def test_show_recipe_ratings_page_error_handling(
    mock_compute, mock_show_details, recipe_df, interaction_df, recipe_stats_df
):
    mock_compute.return_value = pd.DataFrame()  # Aucune recette

    with patch("food_analysis.pages.recipe_ratings.st") as mock_st:
        mock_st.slider.return_value = 10
        mock_st.dataframe.side_effect = Exception("Streamlit error")
        mock_st.columns.return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        mock_st.spinner.__enter__.return_value = None
        mock_st.spinner.__exit__.return_value = None

        # Le test ne doit pas crasher
        recipe_ratings.show_recipe_ratings_page(recipe_df, interaction_df)

        # Comme il y a une erreur dans dataframe, show_recipe_details ne doit pas être appelé
        mock_show_details.assert_not_called()
