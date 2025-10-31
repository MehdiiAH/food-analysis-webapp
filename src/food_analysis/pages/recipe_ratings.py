# mypy: disable-error-code="attr-defined"

import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import streamlit as st

from food_analysis.core.analyzer import compute_recipe_stats, recipe_reviews


def show_recipe_ratings_page(
    recipe_df: pd.DataFrame, interaction_df: pd.DataFrame
) -> None:
    """
    Affiche la page des recettes les mieux notées.

    Args:
        recipe_df: DataFrame des recettes
        interaction_df: DataFrame des interactions
    """
    st.header("🏆 Recettes les Mieux Notées")

    # === BARRE DE RECHERCHE ===
    st.subheader("🔍 Recherche Intelligente")

    col_search, col_clear = st.columns([4, 1])

    with col_search:
        search_query = st.text_input(
            "Rechercher une recette",
            placeholder="Ex: Fajitas with guacamole",
            label_visibility="collapsed",
            key="search_recipe",
        )

    with col_clear:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.search_recipe = ""
            st.rerun()

    # Afficher un message si une recherche est en cours
    if search_query and search_query.strip():
        st.info(f"🔍 Recherche en cours pour : **{search_query}**")

    st.markdown("---")

    # === SIDEBAR : Filtres ===
    with st.sidebar:
        st.subheader("⚙️ Paramètres")

        # Paramètre m pour la pondération
        m = st.slider(
            "Nombre minimal d'avis (m)",
            min_value=5,
            max_value=100,
            value=10,
            step=5,
            help="Paramètre de pondération bayésienne : plus m est élevé, plus les recettes avec peu d'avis sont pénalisées",
        )

        # Nombre de recettes à afficher
        n_recipes = st.slider(
            "Nombre de recettes à afficher",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
        )

    # === CALCUL DES STATISTIQUES ===
    with st.spinner("Calcul des statistiques des recettes..."):
        recipe_stats = compute_recipe_stats(recipe_df, interaction_df, m=m)

        if recipe_stats.empty or "weighted_rating" not in recipe_stats.columns:
            st.error("Impossible de calculer les statistiques de recette.")
            return

        if search_query and search_query.strip():
            recipe_stats = recipe_stats.sample(frac=1, random_state=None).reset_index(
                drop=True
            )

        # Garder seulement les N premières
        top_recipes = recipe_stats.head(n_recipes)

    # === MÉTRIQUES GLOBALES ===
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Recettes",
            f"{len(recipe_df):,}",
            help="Nombre total de recettes dans la base",
        )

    with col2:
        st.metric("Total Avis", f"{len(interaction_df):,}", help="Nombre total d'avis")

    with col3:
        avg_rating = interaction_df[interaction_df["rating"] > 0]["rating"].mean()
        st.metric(
            "Note Moyenne Globale",
            f"{avg_rating:.2f}/5",
            help="Note moyenne de toutes les recettes",
        )

    with col4:
        st.metric(
            "Recettes Affichées",
            f"{len(top_recipes)}",
            help="Nombre de recettes après filtrage",
        )

    st.markdown("---")

    # === TABLEAU INTERACTIF DES RECETTES ===
    st.subheader("📋 Top Recettes")
    st.caption("👆 Cliquez sur une ligne pour voir les détails et les avis")

    # Préparer les données pour l'affichage
    display_df = top_recipes.copy()
    display_df["rank"] = range(1, len(display_df) + 1)

    # Formater les colonnes
    display_df["weighted_rating_display"] = display_df["weighted_rating"].apply(
        lambda x: f"{x:.2f} ⭐"
    )
    display_df["avg_rating_display"] = display_df["avg_rating"].apply(
        lambda x: f"{x:.2f}"
    )

    # Réorganiser les colonnes pour l'affichage
    display_columns = [
        "rank",
        "name",
        "weighted_rating_display",
        "avg_rating_display",
        "n_reviews",
    ]
    display_df_show = display_df[display_columns].copy()

    # === TABLEAU CLIQUABLE ===
    event = st.dataframe(
        display_df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "rank": st.column_config.NumberColumn(
                "Rang", help="Classement de la recette", width="small"
            ),
            "name": st.column_config.TextColumn(
                "Nom de la Recette",
                width="large",
                help="Cliquez sur la ligne pour voir les détails",
            ),
            "weighted_rating_display": st.column_config.TextColumn(
                "Note Pondérée",
                width="medium",
                help="Note pondérée prenant en compte le nombre d'avis",
            ),
            "avg_rating_display": st.column_config.TextColumn(
                "Note Moyenne", width="small", help="Note moyenne brute"
            ),
            "n_reviews": st.column_config.NumberColumn(
                "Nombre d'Avis", format="%d 💬", width="small"
            ),
        },
        on_select="rerun",
        selection_mode="single-row",
        key="recipe_table",
    )

    # === AFFICHAGE DES DÉTAILS ===
    # Vérifier s'il y a une sélection
    selected_recipe_name: str

    # Gestion de la sélection avec vérification de type
    try:
        # Type ignore car streamlit peut ne pas avoir les types à jour
        if (
            hasattr(event, "selection")
            and hasattr(event.selection, "rows")
            and event.selection.rows
        ):  # type: ignore[attr-defined]
            # Une ligne a été cliquée
            selected_idx = event.selection.rows[0]  # type: ignore[attr-defined]
            selected_recipe_name = str(display_df_show.iloc[selected_idx]["name"])
        else:
            # Aucune sélection : afficher la première recette par défaut
            selected_recipe_name = str(display_df_show.iloc[0]["name"])
    except (AttributeError, IndexError, KeyError):
        # En cas d'erreur, afficher la première recette
        selected_recipe_name = str(display_df_show.iloc[0]["name"])

    if selected_recipe_name:
        # Récupérer les infos de la recette sélectionnée
        selected_recipe = top_recipes[top_recipes["name"] == selected_recipe_name].iloc[
            0
        ]

        # Trouver l'ID de la recette dans recipe_df
        recipe_id = recipe_df[recipe_df["name"] == selected_recipe_name]["id"].values[0]

        # Afficher les détails de la recette
        st.markdown("---")
        show_recipe_details(
            recipe_id=recipe_id,  # type: ignore[arg-type]
            recipe_name=selected_recipe_name,
            recipe_stats=selected_recipe,
            recipe_df=recipe_df,
            interaction_df=interaction_df,
        )


def show_recipe_details(
    recipe_id: int,
    recipe_name: str,
    recipe_stats: pd.Series,
    recipe_df: pd.DataFrame,
    interaction_df: pd.DataFrame,
) -> None:
    """
    Affiche les détails d'une recette sélectionnée.

    Args:
        recipe_id: ID de la recette
        recipe_name: Nom de la recette
        recipe_stats: Statistiques de la recette (Series)
        recipe_df: DataFrame des recettes
        interaction_df: DataFrame des interactions
    """
    # Container pour les détails
    with st.container():
        st.markdown(f"### 🍳 {recipe_name}")

        # Informations de la recette depuis recipe_df
        recipe_info = recipe_df[recipe_df["id"] == recipe_id].iloc[0]

        # === INFORMATIONS PRINCIPALES ===
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "⭐ Note Pondérée",
                f"{recipe_stats['weighted_rating']:.2f}",
                help="Note pondérée bayésienne - métrique principale",
            )

        with col2:
            st.metric(
                "Note Moyenne Brute",
                f"{recipe_stats['avg_rating']:.2f}",
                help="Moyenne arithmétique simple des notes",
            )

        with col3:
            st.metric(
                "💬 Nombre d'Avis",
                f"{int(recipe_stats['n_reviews'])}",
                help="Total des avis reçus",
            )

        with col4:
            if "minutes" in recipe_info and pd.notna(recipe_info["minutes"]):
                minutes = recipe_info["minutes"]
                if minutes < 60:
                    time_str = f"{int(minutes)} min"
                else:
                    hours = minutes // 60
                    mins = minutes % 60
                    time_str = f"{int(hours)}h{int(mins):02d}"
                st.metric("⏱️ Temps", time_str)

        st.markdown("---")

        # === AVIS ET COMMENTAIRES ===
        st.subheader("💬 Avis et Commentaires")

        # Récupérer les avis
        reviews = recipe_reviews(recipe_id, interaction_df)

        if len(reviews) == 0:
            st.warning("Aucun avis disponible pour cette recette.")
        else:
            # Filtres pour les avis
            col1, col2 = st.columns([2, 1])

            with col1:
                # Filtre par note
                rating_filter: list[int] = st.multiselect(
                    "Filtrer par note",
                    options=[5, 4, 3, 2, 1, 0],
                    default=[5, 4, 3, 2, 1, 0],
                    format_func=lambda x: f"⭐ {x}" if x > 0 else "❌ Sans note",
                    key=f"rating_filter_{recipe_id}",
                )

            with col2:
                # Nombre d'avis à afficher
                # Adapter min_value et value au nombre d'avis disponibles
                min_reviews = min(5, len(reviews))
                default_reviews = min(10, len(reviews))

                n_reviews_to_show = st.number_input(
                    "Nombre d'avis à afficher",
                    min_value=min_reviews,
                    max_value=len(reviews),
                    value=default_reviews,
                    step=min(5, len(reviews)),
                    key=f"n_reviews_{recipe_id}",
                )

            # Filtrer les avis
            filtered_reviews = reviews[reviews["rating"].isin(rating_filter)].head(
                n_reviews_to_show
            )

            st.info(
                f"📊 Affichage de **{len(filtered_reviews)}** avis sur **{len(reviews)}** au total"
            )

            # === GRAPHIQUE : Distribution des notes ===
            with st.expander(
                "📊 Distribution des Notes pour cette Recette", expanded=False
            ):
                rating_counts = (
                    reviews["rating"].value_counts().sort_index(ascending=False)
                )

                fig = px.bar(
                    x=rating_counts.values,
                    y=[
                        f"⭐ {r}" if r > 0 else "❌ Sans note"
                        for r in rating_counts.index
                    ],
                    orientation="h",
                    labels={"x": "Nombre d'Avis", "y": "Note"},
                    title="Distribution des Notes",
                    color=rating_counts.values,
                    color_continuous_scale="YlOrRd",
                )
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)

            # Afficher les avis
            for _idx, review in filtered_reviews.iterrows():
                with st.container():
                    # Créer une carte pour chaque avis
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        # Afficher les étoiles
                        rating_stars = (
                            "⭐" * int(review["rating"])
                            if review["rating"] > 0
                            else "❌ Sans note"
                        )
                        st.markdown(f"**{rating_stars}**")

                    with col2:
                        # Date de l'avis
                        if pd.notna(review["date"]):
                            try:
                                date = pd.to_datetime(review["date"])
                                st.caption(f"📅 {date.strftime('%d/%m/%Y')}")
                            except Exception:
                                st.caption("📅 Date inconnue")

                    # Commentaire
                    if pd.notna(review["review"]) and str(review["review"]).strip():
                        review_text = str(review["review"]).strip()

                        # Utiliser un style de citation
                        if len(review_text) > 300:
                            st.markdown(f"> {review_text[:300]}...")
                            with st.expander("📖 Lire la suite"):
                                st.markdown(f"> {review_text}")
                        else:
                            st.markdown(f"> {review_text}")
                    else:
                        st.caption("_Aucun commentaire écrit_")

                    # Séparateur subtil
                    st.markdown(
                        "<hr style='margin: 10px 0; border: none; border-top: 1px solid #e0e0e0;'>",
                        unsafe_allow_html=True,
                    )


# Pour tester la page seule (optionnel)
if __name__ == "__main__":
    st.set_page_config(page_title="Recipe Ratings", layout="wide")

    from food_analysis.core.data_loader import DataLoader

    loader = DataLoader()
    recipes = loader.load_recipes()
    interactions = loader.load_interactions()

    show_recipe_ratings_page(recipes, interactions)
