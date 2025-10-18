# tests/unit/test_analyzer.py


import numpy as np
import pandas as pd
import pytest

from food_analysis.core.analyzer import (
    compute_recipe_stats,
    compute_user_stats,
    recipe_reviews,
)

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


@pytest.fixture
def recipe_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Cake", "Soup", "Pizza"],
            "minutes": [30, 20, 45],
            "ingredients": [
                '["flour", "sugar", "eggs"]',
                '["carrot", "water"]',
                '["cheese", "tomato", "flour"]',
            ],
            "steps": ['["mix", "bake"]', '["boil", "serve"]', '["prepare", "bake"]'],
        }
    )


@pytest.fixture
def interaction_df():
    return pd.DataFrame(
        {
            "user_id": [10, 10, 11, 12, 12],
            "recipe_id": [1, 2, 2, 3, 1],
            "rating": [4, 5, 3, 4, 2],
            "date": pd.to_datetime(
                ["2020-01-01", "2020-01-05", "2020-01-10", "2020-02-01", "2020-02-10"]
            ),
            "review": ["good", "great", "ok", "fine", "bad"],
        }
    )


# ---------------------------
# Tests compute_recipe_stats
# ---------------------------
def test_compute_recipe_stats_basic(recipe_df, interaction_df):
    """Vérifie que la fonction renvoie bien un DataFrame trié et cohérent."""
    result = compute_recipe_stats(recipe_df, interaction_df, m=5)
    assert isinstance(result, pd.DataFrame)
    assert set(["name", "avg_rating", "n_reviews", "weighted_rating"]).issubset(
        result.columns
    )
    # Les recettes doivent être triées par weighted_rating décroissant
    assert all(
        result["weighted_rating"].sort_values(ascending=False)
        == result["weighted_rating"]
    )


def test_compute_recipe_stats(sample_recipes, sample_interactions):
    result = compute_recipe_stats(sample_recipes, sample_interactions, m=1)

    # Vérifie les colonnes attendues
    assert set(result.columns) == {"name", "avg_rating", "n_reviews", "weighted_rating"}

    # Vérifie que le nombre de lignes correspond aux recettes avec interactions
    assert len(result) == 3

    # Vérifie que la note pondérée est calculée
    assert all(result["weighted_rating"] > 0)


def test_compute_recipe_stats_empty_df_logs_warning(caplog):
    """Vérifie la gestion de DataFrame vide (mais avec colonnes attendues)."""
    # Crée deux DataFrames vides avec les bonnes colonnes
    empty_recipes = pd.DataFrame(columns=["id", "name"])
    empty_interactions = pd.DataFrame(columns=["recipe_id", "rating"])

    result = compute_recipe_stats(empty_recipes, empty_interactions)

    # Vérifie que le warning a bien été loggé
    assert "vide" in caplog.text.lower()
    # La fonction renvoie un DataFrame vide mais valide
    assert isinstance(result, pd.DataFrame)
    assert all(
        col in result.columns
        for col in ["name", "avg_rating", "n_reviews", "weighted_rating"]
    )
    assert result.empty


def test_compute_recipe_stats_weighting_effect(recipe_df, interaction_df):
    """Plus m est grand, plus la pondération tire vers la moyenne globale."""
    result1 = compute_recipe_stats(recipe_df, interaction_df, m=1)
    result2 = compute_recipe_stats(recipe_df, interaction_df, m=100)
    C = result1["avg_rating"].mean()
    # Avec un grand m, weighted_rating est plus proche de la moyenne globale
    diff1 = abs(result1["weighted_rating"].mean() - C)
    diff2 = abs(result2["weighted_rating"].mean() - C)
    assert diff2 < diff1


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


def test_recipe_reviews_returns_correct_rows(interaction_df):
    """Vérifie qu'on récupère bien les avis du bon recipe_id."""
    result = recipe_reviews(2, interaction_df)
    assert all(result["rating"].isin([5, 3]))
    assert "user_id" in result.columns
    assert result["date"].is_monotonic_decreasing


def test_recipe_reviews_empty_df_logs_warning(caplog):
    """Vérifie la gestion d’un DataFrame vide."""
    df = pd.DataFrame(columns=["recipe_id", "user_id", "rating", "date", "review"])
    result = recipe_reviews(1, df)
    assert "vide" in caplog.text.lower()
    assert isinstance(result, pd.DataFrame)
    # Doit être vide
    assert result.empty


# ============================
#  TESTS : compute_user_stats
# ============================


def test_compute_user_stats_basic(recipe_df, interaction_df):
    """Vérifie les statistiques utilisateur de base."""
    user_stats = compute_user_stats(recipe_df, interaction_df)
    assert "user_id" in user_stats.columns
    assert "n_ratings" in user_stats.columns
    assert "avg_rating_given" in user_stats.columns
    assert "lenient_score" in user_stats.columns
    # Tous les user_id du jeu d’entrée doivent être présents
    assert set(interaction_df["user_id"]) <= set(user_stats["user_id"])


def test_compute_user_stats_numerical_consistency(recipe_df, interaction_df):
    """Vérifie la cohérence des valeurs numériques."""
    user_stats = compute_user_stats(recipe_df, interaction_df)
    assert (user_stats["n_ratings"] > 0).all()
    # Tolérance élargie : ±0.2 autour de 0
    assert np.isclose(user_stats["lenient_score"].mean(), 0, atol=0.2)


def test_compute_user_stats_handles_missing_dates(recipe_df, interaction_df):
    """Vérifie que le code fonctionne même sans la colonne 'date'."""
    df_no_date = interaction_df.drop(columns=["date"])
    stats = compute_user_stats(recipe_df, df_no_date)
    assert "n_days_active" in stats.columns
    assert stats["n_days_active"].isna().any()
