# tests/unit/test_analyzer.py

import pandas as pd
import pytest

from food_analysis.core.analyzer import compute_recipe_stats, recipe_reviews

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
# Tests compute_recipe_stats
# ---------------------------


def test_compute_recipe_stats(sample_recipes, sample_interactions):
    result = compute_recipe_stats(sample_recipes, sample_interactions, m=1)

    # Vérifie les colonnes attendues
    assert set(result.columns) == {"name", "avg_rating", "n_reviews", "weighted_rating"}

    # Vérifie que le nombre de lignes correspond aux recettes avec interactions
    assert len(result) == 3

    # Vérifie que la note pondérée est calculée
    assert all(result["weighted_rating"] > 0)


# ---------------------------
# Tests recipe_reviews
# ---------------------------


def test_recipe_reviews(sample_interactions):
    df_reviews = recipe_reviews(3, sample_interactions)

    # Vérifie que l'ID de recette correspond
    assert all(df_reviews["user_id"].isin([4, 5]))

    # Vérifie que les colonnes sont correctes
    assert list(df_reviews.columns) == ["user_id", "rating", "date", "review"]

    # Vérifie que le tri par date est correct (descendant)
    assert df_reviews.iloc[0]["date"] >= df_reviews.iloc[1]["date"]
