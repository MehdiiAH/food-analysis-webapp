# tests/test_data_analyzer.py
from unittest.mock import patch

import pandas as pd
import pytest

from food_analysis.core.analyzer import DataAnalyzer


@pytest.fixture
def sample_interactions() -> pd.DataFrame:
    """Crée un petit DataFrame de test pour les interactions."""
    return pd.DataFrame(
        {
            "recipe_id": [1, 1, 1, 2, 2, 3],
            "rating": [5, 4, 3, 5, 0, 2],
        }
    )


def test_plot_rating_distribution_valid(sample_interactions: pd.DataFrame) -> None:
    """Teste que la méthode appelle correctement plt.hist et plt.show."""
    analyzer = DataAnalyzer()

    with patch("food_analysis.core.data_analyzer.plt") as mock_plt:
        analyzer.plot_rating_distribution(sample_interactions, recipe_id=1)

        # Vérifie que plt.hist a bien été appelé avec les bonnes notes
        ratings = sample_interactions.loc[
            sample_interactions["recipe_id"] == 1, "rating"
        ]
        mock_plt.hist.assert_called_once_with(ratings, bins=6, edgecolor="black")

        # Vérifie que les autres fonctions de matplotlib ont été appelées
        mock_plt.title.assert_called_once()
        mock_plt.xlabel.assert_called_once_with("Note")
        mock_plt.ylabel.assert_called_once_with("Nombre d'avis")
        mock_plt.show.assert_called_once()


def test_plot_rating_distribution_no_ratings() -> None:
    """Teste le cas où la recette n’a pas de notes."""
    analyzer = DataAnalyzer()
    empty_df = pd.DataFrame({"recipe_id": [], "rating": []})

    with patch("food_analysis.core.data_analyzer.plt") as mock_plt:
        analyzer.plot_rating_distribution(empty_df, recipe_id=42)

        # Même sans données, la méthode doit quand même appeler plt.hist (avec une série vide)
        mock_plt.hist.assert_called_once()
        mock_plt.show.assert_called_once()
