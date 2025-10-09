# tests/unit/test_data_analyzer.py
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


def test_plot_rating_distribution_calls_plt(sample_interactions):
    analyzer = DataAnalyzer()

    with (
        patch("food_analysis.core.analyzer.plt.hist") as mock_hist,
        patch("food_analysis.core.analyzer.plt.show") as mock_show,
        patch("food_analysis.core.analyzer.plt.title") as mock_title,
        patch("food_analysis.core.analyzer.plt.xlabel") as mock_xlabel,
        patch("food_analysis.core.analyzer.plt.ylabel") as mock_ylabel,
        patch("food_analysis.core.analyzer.plt.xlim") as mock_xlim,
    ):
        analyzer.plot_rating_distribution(sample_interactions, recipe_id=1)

        # Convertir la Series en liste pour comparer
        expected_ratings = sample_interactions.loc[
            sample_interactions["recipe_id"] == 1, "rating"
        ].tolist()

        args, kwargs = mock_hist.call_args
        assert list(args[0]) == expected_ratings
        assert kwargs["bins"] == 6
        assert kwargs["edgecolor"] == "black"

        mock_title.assert_called_once_with("Distribution des notes pour la recette 1")
        mock_xlabel.assert_called_once_with("Note")
        mock_ylabel.assert_called_once_with("Nombre d'avis")
        mock_xlim.assert_called_once_with(-0.25, None)
        mock_show.assert_called_once()


def test_plot_rating_distribution_no_ratings() -> None:
    """Teste le cas où la recette n'a pas de notes."""
    analyzer = DataAnalyzer()
    empty_df = pd.DataFrame({"recipe_id": [], "rating": []})

    with patch("food_analysis.core.analyzer.plt") as mock_plt:
        analyzer.plot_rating_distribution(empty_df, recipe_id=42)

        # Même sans données, plt.hist et plt.show doivent être appelés
        mock_plt.hist.assert_called_once()
        mock_plt.show.assert_called_once()
