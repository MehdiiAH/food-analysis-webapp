# tests/unit/test_note_et_avis.py
from unittest.mock import patch

import pandas as pd
import pytest

import food_analysis.core.note_et_avis as nea

# ---------------------------
# Fixtures pour les données
# ---------------------------


@pytest.fixture
def sample_recipes():
    return pd.DataFrame({"id": [1, 2, 3], "name": ["Pasta", "Pizza", "Salad"]})


@pytest.fixture
def sample_interactions():
    return pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4, 5],
            "recipe_id": [1, 1, 2, 3, 3],
            "rating": [5, 4, 3, 2, 1],
            "date": [
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
                "2023-01-04",
                "2023-01-05",
            ],
            "review": ["Good", "Ok", "Nice", "Bad", "Meh"],
        }
    )


# ---------------------------
# Tests load_recipes / load_interactions
# ---------------------------


@patch("pandas.read_csv")
def test_load_recipes(mock_read_csv):
    df_mock = pd.DataFrame({"id": [1], "name": ["Pasta"]})
    mock_read_csv.return_value = df_mock
    result = nea.load_recipes("fake_path.csv")
    mock_read_csv.assert_called_once_with("fake_path.csv")
    pd.testing.assert_frame_equal(result, df_mock)


@patch("pandas.read_csv")
def test_load_interactions(mock_read_csv):
    df_mock = pd.DataFrame({"recipe_id": [1], "rating": [5]})
    mock_read_csv.return_value = df_mock
    result = nea.load_interactions("fake_path.csv")
    mock_read_csv.assert_called_once_with("fake_path.csv")
    pd.testing.assert_frame_equal(result, df_mock)


# ---------------------------
# Tests compute_recipe_stats
# ---------------------------


def test_compute_recipe_stats(sample_recipes, sample_interactions):
    result = nea.compute_recipe_stats(sample_recipes, sample_interactions, m=1)

    # Vérifie les colonnes attendues
    assert set(result.columns) == {"name", "avg_rating", "n_reviews", "weighted_rating"}

    # Vérifie que le nombre de lignes correspond aux recettes avec interactions
    assert len(result) == 3

    # Vérifie que la note pondérée est calculée
    assert all(result["weighted_rating"] > 0)


# ---------------------------
# Tests plot_rating_distribution
# ---------------------------


def test_plot_rating_distribution_calls(sample_interactions):
    with (
        patch("food_analysis.core.note_et_avis.plt.hist") as mock_hist,
        patch("food_analysis.core.note_et_avis.plt.show") as mock_show,
        patch("food_analysis.core.note_et_avis.plt.title") as mock_title,
        patch("food_analysis.core.note_et_avis.plt.xlabel") as mock_xlabel,
        patch("food_analysis.core.note_et_avis.plt.ylabel") as mock_ylabel,
        patch("food_analysis.core.note_et_avis.plt.xlim") as mock_xlim,
    ):
        nea.plot_rating_distribution(sample_interactions, recipe_id=1)

        expected_ratings = sample_interactions.loc[
            sample_interactions["recipe_id"] == 1, "rating"
        ].tolist()
        args, kwargs = mock_hist.call_args
        assert list(args[0]) == expected_ratings
        assert kwargs["bins"] == 6
        assert kwargs["edgecolor"] == "black"
        mock_title.assert_called_once()
        mock_xlabel.assert_called_once()
        mock_ylabel.assert_called_once()
        mock_xlim.assert_called_once()
        mock_show.assert_called_once()


# ---------------------------
# Tests recipe_reviews
# ---------------------------


def test_recipe_reviews(sample_interactions):
    df_reviews = nea.recipe_reviews(3, sample_interactions)

    # Vérifie que l'ID de recette correspond
    assert all(df_reviews["user_id"].isin([4, 5]))

    # Vérifie que les colonnes sont correctes
    assert list(df_reviews.columns) == ["user_id", "rating", "date", "review"]

    # Vérifie que le tri par date est correct (descendant)
    assert df_reviews.iloc[0]["date"] >= df_reviews.iloc[1]["date"]
