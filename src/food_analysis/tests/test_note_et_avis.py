# tests/test_data_utils.py

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from food_analysis.core.note_et_avis import (
    compute_recipe_stats,
    load_interactions,
    load_recipes,
    plot_rating_distribution,
    recipe_reviews,
)

# ==========================================================
#  🔹 TESTS - Chargement des données
# ==========================================================


def test_load_recipes(tmp_path: Path) -> None:
    """Vérifie que load_recipes charge correctement un CSV."""
    csv_path = tmp_path / "RAW_recipes.csv"
    df_expected = pd.DataFrame({"id": [1, 2], "name": ["Cake", "Salad"]})
    df_expected.to_csv(csv_path, index=False)

    df_loaded = load_recipes(str(csv_path))

    pd.testing.assert_frame_equal(df_loaded, df_expected)


def test_load_interactions(tmp_path: Path) -> None:
    """Vérifie que load_interactions charge correctement un CSV."""
    csv_path = tmp_path / "RAW_interactions.csv"
    df_expected = pd.DataFrame(
        {
            "recipe_id": [1, 1, 2],
            "rating": [5, 4, 3],
            "user_id": [10, 20, 30],
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "review": ["Excellent", "Bon", "Moyen"],
        }
    )
    df_expected.to_csv(csv_path, index=False)

    df_loaded = load_interactions(str(csv_path))
    pd.testing.assert_frame_equal(df_loaded, df_expected)


# ==========================================================
#  🔹 TESTS - Calculs statistiques
# ==========================================================


def test_compute_recipe_stats_basic() -> None:
    """Teste le calcul de la note moyenne et pondérée."""
    recipe_df = pd.DataFrame({"id": [1, 2], "name": ["Cake", "Pizza"]})
    interaction_df = pd.DataFrame({"recipe_id": [1, 1, 2, 2], "rating": [5, 4, 3, 1]})

    result = compute_recipe_stats(recipe_df, interaction_df, m=1)

    # Vérifie la structure
    assert list(result.columns) == [
        "name",
        "avg_rating",
        "n_reviews",
        "weighted_rating",
    ]
    assert "Cake" in result["name"].values
    assert "Pizza" in result["name"].values

    # Vérifie que la moyenne est correcte
    avg_cake = result.loc[result["name"] == "Cake", "avg_rating"].values[0]
    assert pytest.approx(avg_cake, 0.01) == 4.5


def test_compute_recipe_stats_sorting() -> None:
    """Vérifie que les recettes sont triées par note pondérée décroissante."""
    recipe_df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
    interaction_df = pd.DataFrame({"recipe_id": [1, 1, 2], "rating": [5, 5, 1]})

    result = compute_recipe_stats(recipe_df, interaction_df)
    assert result.iloc[0]["name"] == "A"


# ==========================================================
#  🔹 TESTS - Visualisation
# ==========================================================


@patch("food_analysis.core.data_utils.plt")
def test_plot_rating_distribution(mock_plt: MagicMock) -> None:
    """Teste que la fonction trace bien l’histogramme sans erreur."""
    df = pd.DataFrame({"recipe_id": [1, 1, 2], "rating": [5, 4, 3]})

    plot_rating_distribution(df, recipe_id=1)

    mock_plt.hist.assert_called_once()
    mock_plt.title.assert_called_with("Distribution des notes pour la recette 1")
    mock_plt.show.assert_called_once()


# ==========================================================
#  🔹 TESTS - Extraction des avis
# ==========================================================


def test_recipe_reviews_returns_correct_rows() -> None:
    """Vérifie que seuls les avis du bon recipe_id sont retournés."""
    interaction_df = pd.DataFrame(
        {
            "recipe_id": [1, 1, 2],
            "user_id": [10, 20, 30],
            "rating": [5, 4, 3],
            "date": ["2023-01-01", "2023-01-03", "2023-01-02"],
            "review": ["Excellent", "Bon", "Ok"],
        }
    )

    result = recipe_reviews(1, interaction_df)

    # Vérifie que seules les lignes pour recipe_id == 1 sont retournées
    assert (result["user_id"] == [20, 10]).all()  # trié par date décroissante
    assert len(result) == 2
    assert list(result.columns) == ["user_id", "rating", "date", "review"]
