"""Tests unitaires pour visualization.py"""

import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, "src")

from food_analysis.pages.visualizations import show_visualization_page


@pytest.fixture
def sample_recipes_df():
    """DataFrame de recettes pour les tests."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Recette A", "Recette B", "Recette C"],
            "minutes": [30, 45, 60],
        }
    )


@pytest.fixture
def sample_interactions_df():
    """DataFrame d'interactions pour les tests."""
    return pd.DataFrame(
        {
            "recipe_id": [1, 1, 2, 2, 3, 3, 1, 2],
            "user_id": [10, 20, 10, 30, 20, 30, 10, 30],
            "rating": [5, 4, 3, 5, 4, 2, 5, 4],
            "date": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                    "2025-01-03",
                    "2025-01-04",
                    "2025-01-05",
                    "2025-01-06",
                    "2025-01-07",
                    "2025-01-08",
                ]
            ),
            "review": [
                "Super!",
                "Bien",
                "Ok",
                "Excellent",
                "Bon",
                "Moyen",
                "Parfait",
                "Sympa",
            ],
        }
    )


def test_show_visualization_page_basic(sample_recipes_df, sample_interactions_df):
    """Test le fonctionnement de base de la page de visualisation."""
    with (
        patch("food_analysis.pages.visualizations.st") as mock_st,
        patch("food_analysis.pages.visualizations.plt") as mock_plt,
    ):
        # Configuration des mocks de base
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None
        mock_st.write.return_value = None
        mock_st.metric.return_value = None
        mock_st.pyplot.return_value = None

        # Mock des colonnes et contrôles interactifs
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Configuration des contrôles interactifs avec valeurs par défaut
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)

        mock_st.checkbox.return_value = False  # log_x
        mock_st.number_input.return_value = 2000  # x_limit
        mock_st.slider.return_value = 0.1  # jitter

        # Mock matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_scatter = MagicMock()
        mock_ax.scatter.return_value = mock_scatter
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Appel de la fonction
        show_visualization_page(sample_recipes_df, sample_interactions_df)

        # Vérifications
        mock_st.header.assert_called_once()
        assert mock_st.markdown.call_count >= 1
        mock_st.columns.assert_called()
        mock_st.checkbox.assert_called_once()
        mock_st.number_input.assert_called_once()
        mock_st.slider.assert_called_once()
        mock_plt.subplots.assert_called_once()
        mock_st.pyplot.assert_called_once()
        mock_st.metric.assert_called()


def test_show_visualization_page_with_log_scale(
    sample_recipes_df, sample_interactions_df
):
    """Test avec l'échelle logarithmique activée."""
    with (
        patch("food_analysis.pages.visualizations.st") as mock_st,
        patch("food_analysis.pages.visualizations.plt") as mock_plt,
    ):
        # Configuration des mocks
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None
        mock_st.write.return_value = None
        mock_st.metric.return_value = None
        mock_st.pyplot.return_value = None

        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)

        # LOG SCALE ACTIVÉ
        mock_st.checkbox.return_value = True
        mock_st.number_input.return_value = 2000
        mock_st.slider.return_value = 0.1

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_scatter = MagicMock()
        mock_ax.scatter.return_value = mock_scatter
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Appel de la fonction
        show_visualization_page(sample_recipes_df, sample_interactions_df)

        # Vérifie que set_xscale('log') a été appelé
        mock_ax.set_xscale.assert_called_once_with("log")


def test_show_visualization_page_with_custom_limits(
    sample_recipes_df, sample_interactions_df
):
    """Test avec des limites personnalisées."""
    with (
        patch("food_analysis.pages.visualizations.st") as mock_st,
        patch("food_analysis.pages.visualizations.plt") as mock_plt,
    ):
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None
        mock_st.write.return_value = None
        mock_st.metric.return_value = None
        mock_st.pyplot.return_value = None

        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)

        mock_st.checkbox.return_value = False
        mock_st.number_input.return_value = 5000  # LIMITE PERSONNALISÉE
        mock_st.slider.return_value = 0.2  # JITTER PERSONNALISÉ

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_scatter = MagicMock()
        mock_ax.scatter.return_value = mock_scatter
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        show_visualization_page(sample_recipes_df, sample_interactions_df)

        # Vérifie que set_xlim a été appelé avec la bonne valeur
        mock_ax.set_xlim.assert_called_once_with(0, 5000)


def test_show_visualization_page_with_jitter(sample_recipes_df, sample_interactions_df):
    """Test que le jitter est appliqué correctement."""
    with (
        patch("food_analysis.pages.visualizations.st") as mock_st,
        patch("food_analysis.pages.visualizations.plt") as mock_plt,
        patch("food_analysis.pages.visualizations.np.random") as mock_random,
    ):
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None
        mock_st.write.return_value = None
        mock_st.metric.return_value = None
        mock_st.pyplot.return_value = None

        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)

        mock_st.checkbox.return_value = False
        mock_st.number_input.return_value = 2000
        mock_st.slider.return_value = 0.3  # JITTER > 0

        # Mock pour le jitter
        mock_random.seed.return_value = None
        mock_random.uniform.return_value = np.array([0.1, -0.05, 0.15])

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_scatter = MagicMock()
        mock_ax.scatter.return_value = mock_scatter
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        show_visualization_page(sample_recipes_df, sample_interactions_df)

        # Vérifie que le seed et uniform ont été appelés
        mock_random.seed.assert_called_once_with(42)
        mock_random.uniform.assert_called_once()


def test_show_visualization_page_empty_dataframe():
    """Test avec un DataFrame d'interactions vide."""
    empty_recipes = pd.DataFrame(columns=["id", "name", "minutes"])
    empty_interactions = pd.DataFrame(
        columns=["recipe_id", "user_id", "rating", "date", "review"]
    )

    with (
        patch("food_analysis.pages.visualizations.st") as mock_st,
        patch("food_analysis.pages.visualizations.plt") as mock_plt,
    ):
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None
        mock_st.write.return_value = None
        mock_st.metric.return_value = None
        mock_st.pyplot.return_value = None

        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)

        mock_st.checkbox.return_value = False
        mock_st.number_input.return_value = 2000
        mock_st.slider.return_value = 0.1

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_scatter = MagicMock()
        mock_ax.scatter.return_value = mock_scatter
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Ne devrait pas lever d'erreur
        show_visualization_page(empty_recipes, empty_interactions)

        # Vérifie que la fonction s'exécute quand même
        mock_st.header.assert_called_once()


def test_show_visualization_page_metrics_displayed(
    sample_recipes_df, sample_interactions_df
):
    """Test que les métriques sont correctement affichées."""
    with (
        patch("food_analysis.pages.visualizations.st") as mock_st,
        patch("food_analysis.pages.visualizations.plt") as mock_plt,
    ):
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None
        mock_st.write.return_value = None
        mock_st.metric.return_value = None
        mock_st.pyplot.return_value = None

        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=False)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=False)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=False)

        mock_st.checkbox.return_value = False
        mock_st.number_input.return_value = 2000
        mock_st.slider.return_value = 0.1

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_scatter = MagicMock()
        mock_ax.scatter.return_value = mock_scatter
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        show_visualization_page(sample_recipes_df, sample_interactions_df)

        # Vérifie que st.metric a été appelé au moins 2 fois (pour les 2 métriques)
        assert mock_st.metric.call_count >= 2
