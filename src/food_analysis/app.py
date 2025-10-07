"""Main Streamlit application."""

from typing import Tuple

import pandas as pd
import streamlit as st

from food_analysis.core.data_loader import DataLoader
from food_analysis.pages.recipe_ratings import show_recipe_ratings_page


def main() -> None:
    """Point d'entrée principal de l'application."""
    # Configuration de la page
    st.set_page_config(
        page_title="Food Analysis WebApp",
        page_icon="🍳",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Titre principal
    st.title("🍳 Food.com - Analyse de Données")
    st.markdown("**Version:** 0.1.0")
    st.markdown("---")

    # === CHARGEMENT DES DONNÉES ===
    @st.cache_data
    def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Charge les données depuis les CSV."""
        loader = DataLoader()
        recipes = loader.load_recipes()
        interactions = loader.load_interactions()
        return recipes, interactions

    try:
        with st.spinner("Chargement des données..."):
            recipes_df, interactions_df = load_data()

        # === SIDEBAR : NAVIGATION ===
        with st.sidebar:
            st.header("🧭 Navigation")

            page = st.radio(
                "Sélectionnez une page :",
                ["🏠 Accueil", "🏆 Recettes les Mieux Notées", "ℹ️ À propos"],
                index=0,
            )

            st.markdown("---")
            st.markdown("### 📊 Informations")
            st.metric("Nombre de recettes", f"{len(recipes_df):,}")
            st.metric("Nombre d'interactions", f"{len(interactions_df):,}")

        # === ROUTING DES PAGES ===
        if page == "🏠 Accueil":
            show_home_page(recipes_df, interactions_df)

        elif page == "🏆 Recettes les Mieux Notées":
            show_recipe_ratings_page(recipes_df, interactions_df)

        else:  # À propos
            show_about_page()

    except FileNotFoundError as e:
        st.error(f"""
        ❌ **Erreur : Fichiers de données non trouvés**

        {str(e)}

        Veuillez télécharger les données depuis Kaggle et les placer dans `data/raw/`:
        - RAW_recipes.csv
        - RAW_interactions.csv

        [Télécharger les données](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)
        """)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {str(e)}")
        st.exception(e)


def show_home_page(recipes_df: pd.DataFrame, interactions_df: pd.DataFrame) -> None:
    """Affiche la page d'accueil."""
    st.header("Bienvenue sur l'application d'analyse Food.com")

    st.markdown("""
    ### 🎯 Objectif du projet

    Cette application permet d'explorer et d'analyser les données de recettes
    et d'interactions utilisateurs provenant de Food.com.

    ### 📊 Fonctionnalités

    - **🏆 Recettes les Mieux Notées** : Découvrez les recettes les plus populaires avec un système de notation pondérée

    ### 🚀 Comment utiliser

    Utilisez le menu de navigation à gauche pour explorer les différentes sections.
    """)

    # Quelques statistiques rapides
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_rating = interactions_df[interactions_df["rating"] > 0]["rating"].mean()
        st.metric("📊 Note Moyenne Globale", f"{avg_rating:.2f}/5")

    with col2:
        avg_reviews = interactions_df.groupby("recipe_id").size().mean()
        st.metric("💬 Moyenne d'Avis par Recette", f"{avg_reviews:.1f}")

    with col3:
        unique_users = interactions_df["user_id"].nunique()
        st.metric("👥 Utilisateurs Actifs", f"{unique_users:,}")


def show_about_page() -> None:
    """Affiche la page À propos."""
    st.header("ℹ️ À propos")

    st.markdown("""
    ### 📚 À propos du projet

    Ce projet a été développé dans le cadre d'un cours sur le développement
    Python pour la production.

    ### 🔗 Ressources

    - [Dataset Kaggle](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)
    - [Documentation](https://github.com/MehdiiAH/food-analysis-webapp)

    ### 👥 Équipe

    Projet développé en équipe.
    """)


if __name__ == "__main__":
    main()
