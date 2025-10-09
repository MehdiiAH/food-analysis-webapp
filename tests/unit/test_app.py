import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.insert(0, "src")

import food_analysis.app as main_module

print(main_module.main)


def test_main_exists():
    assert callable(main_module.main)


@pytest.fixture
def sample_recipes_df():
    return pd.DataFrame(
        {"id": [1, 2], "name": ["Recette A", "Recette B"], "minutes": [30, 90]}
    )


@pytest.fixture
def sample_interactions_df():
    return pd.DataFrame(
        {
            "recipe_id": [1, 1, 2],
            "user_id": [10, 20, 30],
            "rating": [5, 4, 3],
            "date": ["2025-10-01", "2025-10-02", "2025-10-03"],
            "review": ["Super!", "Bien", "Ok"],
        }
    )


def mock_load_data(recipes_df, interactions_df):
    """Retourne une fonction qui renvoie les dataframes mockés"""

    def inner():
        return recipes_df, interactions_df

    return inner


def test_main_normal(sample_recipes_df, sample_interactions_df):
    with patch("food_analysis.app.st") as mock_st:
        # Mock complet des contextes Streamlit
        mock_st.spinner.return_value.__enter__.return_value = None
        mock_st.sidebar.__enter__.return_value = mock_st.sidebar
        mock_st.radio.return_value = "🏠 Accueil"
        mock_st.metric.return_value = None
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.set_page_config.return_value = None
        mock_st.title.return_value = None
        mock_st.markdown.return_value = None
        mock_st.error.return_value = None
        mock_st.exception.return_value = None

        # Mock de st.cache_data pour le chargement des données
        mock_st.cache_data.return_value = mock_load_data(
            sample_recipes_df, sample_interactions_df
        )

        main_module.main()

        # Vérifications simples
        mock_st.radio.assert_called_once()
        mock_st.set_page_config.assert_called_once()
        mock_st.title.assert_called_once()
        mock_st.metric.assert_called()


def test_main_file_not_found():
    with patch("food_analysis.app.st") as mock_st:
        # Simule FileNotFoundError
        mock_st.spinner.return_value.__enter__.return_value = None
        mock_st.sidebar.__enter__.return_value = mock_st.sidebar
        mock_st.radio.return_value = "🏆 Recettes les Mieux Notées"
        mock_st.set_page_config.return_value = None
        mock_st.title.return_value = None
        mock_st.markdown.return_value = None
        mock_st.error.return_value = None
        mock_st.exception.return_value = None

        def load_data_fail():
            raise FileNotFoundError("Fichier manquant")

        mock_st.cache_data.return_value = load_data_fail

        main_module.main()

        # Vérifie que st.error a été appelé
        mock_st.error.assert_called()
        mock_st.exception.assert_not_called()  # car c'est FileNotFoundError, pas Exception


def test_show_home_page(sample_recipes_df, sample_interactions_df):
    with patch("food_analysis.app.st") as mock_st:
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.metric.return_value = None
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None

        main_module.show_home_page(sample_recipes_df, sample_interactions_df)

        mock_st.header.assert_called_once()
        mock_st.columns.assert_called_once()
        mock_st.metric.assert_called()


def test_show_about_page():
    with patch("food_analysis.app.st") as mock_st:
        mock_st.header.return_value = None
        mock_st.markdown.return_value = None

        main_module.show_about_page()

        mock_st.header.assert_called_once()
        mock_st.markdown.assert_called()
