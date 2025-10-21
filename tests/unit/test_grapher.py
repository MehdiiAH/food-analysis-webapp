from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from food_analysis.core.grapher import plot_activity_vs_leniency


@pytest.fixture
def sample_df():
    """Crée un DataFrame d'exemple."""
    return pd.DataFrame(
        {
            "n_ratings": [1, 5, 10, 0, np.nan],
            "lenient_score": [0.2, 0.5, 0.8, 0.9, np.nan],
        }
    )


@patch("food_analysis.core.grapher.plt")
def test_plot_basic(mock_plt, sample_df):
    """Test de base : vérifie que plt.scatter est bien appelé."""
    plot_activity_vs_leniency(sample_df)
    mock_plt.scatter.assert_called_once()
    mock_plt.title.assert_called_with(
        "Relation activité (n_ratings) vs sévérité (lenient_score)"
    )
    mock_plt.xlabel.assert_called_with("Nombre de recettes notées (n_ratings)")
    mock_plt.ylabel.assert_called_with("Leniency score")
    mock_plt.show.assert_called_once()


@patch("food_analysis.core.grapher.plt")
def test_plot_with_logx(mock_plt, sample_df):
    """Vérifie que log_x=True applique bien une échelle logarithmique."""
    plot_activity_vs_leniency(sample_df, log_x=True)
    mock_plt.xscale.assert_called_once_with("log")


@patch("food_analysis.core.grapher.plt")
def test_plot_with_xlim(mock_plt, sample_df):
    """Vérifie que la limite x est bien appliquée."""
    plot_activity_vs_leniency(sample_df, x_limit=20)
    mock_plt.xlim.assert_called_once_with(0, 20)


@patch("food_analysis.core.grapher.plt")
def test_plot_drops_invalid_rows(mock_plt):
    """Vérifie que les lignes avec NaN ou n_ratings <= 0 sont ignorées."""
    df = pd.DataFrame({"n_ratings": [0, np.nan, 5], "lenient_score": [0.5, 0.7, 0.9]})
    plot_activity_vs_leniency(df)
    args, kwargs = mock_plt.scatter.call_args
    x_vals = args[0]
    assert all(x_vals > 0), "Les valeurs <= 0 doivent être exclues"
    assert len(x_vals) == 1, "Seule la ligne valide doit être tracée"


@patch("food_analysis.core.grapher.plt")
def test_plot_handles_empty_df(mock_plt):
    """Vérifie qu’aucune erreur n’est levée avec un DataFrame vide."""
    df_empty = pd.DataFrame(columns=["n_ratings", "lenient_score"])
    plot_activity_vs_leniency(df_empty)
    # Même si vide, il doit tenter de créer une figure
    mock_plt.figure.assert_called_once()
