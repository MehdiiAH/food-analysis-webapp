from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

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
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "review": ["bon", "moyen", "ok", "top", "super"],
        }
    )


@pytest.fixture
def recipe_stats_df():
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

    with patch("food_analysis.pages.recipe_ratings.st") as mock_st:
        mock_st.slider.return_value = 10
        mock_st.dataframe.return_value.selection.rows = [0]

        # Mock dynamique pour st.columns
        def columns_side_effect(arg):
            if arg == [4, 1]:
                return [MagicMock(), MagicMock()]
            elif arg == 4:
                return [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            return [MagicMock(), MagicMock()]

        mock_st.columns.side_effect = columns_side_effect

        mock_st.spinner.__enter__.return_value = None
        mock_st.spinner.__exit__.return_value = None

        recipe_ratings.show_recipe_ratings_page(recipe_df, interaction_df)

    mock_compute.assert_called_once()
    mock_show_details.assert_called_once()  # ✅ le comportement réel


@patch("food_analysis.pages.recipe_ratings.show_recipe_details")
@patch("food_analysis.pages.recipe_ratings.compute_recipe_stats")
def test_show_recipe_ratings_page_no_selection(
    mock_compute, mock_show_details, recipe_df, interaction_df, recipe_stats_df
):
    mock_compute.return_value = recipe_stats_df

    with patch("food_analysis.pages.recipe_ratings.st") as mock_st:
        mock_st.slider.return_value = 10
        mock_st.dataframe.return_value.selection.rows = []

        def columns_side_effect(arg):
            if arg == [4, 1]:
                return [MagicMock(), MagicMock()]
            elif arg == 4:
                return [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            return [MagicMock(), MagicMock()]

        mock_st.columns.side_effect = columns_side_effect
        mock_st.spinner.__enter__.return_value = None
        mock_st.spinner.__exit__.return_value = None

        recipe_ratings.show_recipe_ratings_page(recipe_df, interaction_df)

    mock_compute.assert_called_once()
    mock_show_details.assert_called_once()
