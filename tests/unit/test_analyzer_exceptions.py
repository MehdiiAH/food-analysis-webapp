import numpy as np
import pandas as pd
import pytest

from food_analysis.core.analyzer import (
    compute_recipe_stats,
    compute_user_stats,
    recipe_reviews,
)

# ===============================================================
# === TESTS DES CAS D'ERREUR ET EXCEPTIONS =======================
# ===============================================================


def test_compute_recipe_stats_empty_df_logs_warning(caplog):
    """Doit logger un warning si l'un des DataFrames est vide."""
    recipes = pd.DataFrame(columns=["id", "name"])
    interactions = pd.DataFrame(columns=["recipe_id", "rating"])

    result = compute_recipe_stats(recipes, interactions)

    assert "vide" in caplog.text.lower()
    assert isinstance(result, pd.DataFrame)
    assert all(
        col in result.columns
        for col in ["name", "avg_rating", "n_reviews", "weighted_rating"]
    )
    assert result.empty


def test_compute_recipe_stats_missing_columns_raises_keyerror():
    """Doit lever KeyError si les colonnes requises sont absentes."""
    recipes = pd.DataFrame({"title": ["R1", "R2"]})
    interactions = pd.DataFrame({"id_recette": [1, 2], "rating": [4, 5]})

    with pytest.raises(KeyError):
        compute_recipe_stats(recipes, interactions)


def test_compute_recipe_stats_invalid_types_raises_typeerror():
    """Si la colonne rating contient des types non numériques, Pandas doit lever une erreur."""
    recipes = pd.DataFrame({"id": [1], "name": ["Cake"]})
    interactions = pd.DataFrame({"recipe_id": [1], "rating": ["five"]})

    with pytest.raises(TypeError):
        compute_recipe_stats(recipes, interactions)


# ===============================================================
# === recipe_reviews ============================================
# ===============================================================


def test_recipe_reviews_empty_df_logs_warning(caplog):
    """Doit logger un warning si interaction_df est vide."""
    interactions = pd.DataFrame(
        columns=["recipe_id", "user_id", "rating", "date", "review"]
    )

    result = recipe_reviews(123, interactions)
    assert "vide" in caplog.text.lower()
    assert result.empty


def test_recipe_reviews_missing_columns_raises_keyerror():
    """Doit lever KeyError si les colonnes nécessaires sont absentes."""
    interactions = pd.DataFrame({"user": [1, 2], "note": [4, 5]})
    with pytest.raises(KeyError):
        recipe_reviews(1, interactions)


def test_recipe_reviews_filters_by_recipe_id():
    """Doit renvoyer uniquement les avis de la recette spécifiée."""
    interactions = pd.DataFrame(
        {
            "recipe_id": [1, 1, 2],
            "user_id": [10, 11, 12],
            "rating": [4, 5, 3],
            "date": pd.to_datetime(["2021-01-02", "2021-01-03", "2021-01-01"]),
            "review": ["ok", "super", "bof"],
        }
    )
    result = recipe_reviews(1, interactions)

    assert len(result) == 2
    assert result["user_id"].tolist() == [11, 10]  # tri par date décroissante


# ===============================================================
# === compute_user_stats ========================================
# ===============================================================


def test_compute_user_stats_handles_missing_values():
    """Doit gérer les NaN sans planter."""
    recipes = pd.DataFrame(
        {
            "id": [1],
            "ingredients": [None],
            "steps": [None],
            "minutes": [30],
        }
    )
    interactions = pd.DataFrame(
        {
            "user_id": [1, 1],
            "recipe_id": [1, 1],
            "rating": [np.nan, 5],
            "date": [None, "2021-01-01"],
        }
    )

    result = compute_user_stats(recipes, interactions)
    assert "lenient_score" in result.columns
    assert not result.empty


def test_compute_user_stats_missing_columns_raises_keyerror():
    """Doit lever KeyError si des colonnes nécessaires manquent."""
    recipes = pd.DataFrame({"id": [1]})
    interactions = pd.DataFrame({"user": [1], "note": [4]})
    with pytest.raises(KeyError):
        compute_user_stats(recipes, interactions)


def test_compute_user_stats_empty_inputs():
    """Doit retourner DataFrame vide si interactions est vide."""
    recipes = pd.DataFrame(
        {
            "id": [1],
            "ingredients": ["['sugar']"],
            "steps": ["['mix']"],
            "minutes": [5],
        }
    )
    interactions = pd.DataFrame(columns=["user_id", "recipe_id", "rating"])
    result = compute_user_stats(recipes, interactions)
    assert isinstance(result, pd.DataFrame)
    assert result.empty or all(
        col in result.columns for col in ["user_id", "n_ratings"]
    )


def test_compute_user_stats_invalid_date_formats():
    """Doit convertir les dates invalides sans planter."""
    recipes = pd.DataFrame(
        {
            "id": [1],
            "ingredients": ["['eggs']"],
            "steps": ["['cook']"],
            "minutes": [20],
        }
    )
    interactions = pd.DataFrame(
        {
            "user_id": [1],
            "recipe_id": [1],
            "rating": [5],
            "date": ["not-a-date"],
        }
    )

    result = compute_user_stats(recipes, interactions)
    assert "n_days_active" in result.columns
    assert np.isnan(result["n_days_active"].iloc[0])
