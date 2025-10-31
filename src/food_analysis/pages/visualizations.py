"""Page Streamlit : Visualisation de l'activité et de la sévérité des utilisateurs."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


def show_visualization_page(
    recipes_df: pd.DataFrame, interactions_df: pd.DataFrame
) -> None:
    """Affiche la page de visualisation."""

    st.header("📈 Visualisation des utilisateurs : activité vs sévérité")

    st.markdown("""
    Cette visualisation montre la relation entre :
    - **l'activité** d'un utilisateur (nombre d'avis laissés), et
    - **sa sévérité moyenne** (score de clémence / sévérité basé sur les notes qu'il donne).
    """)

    # === Préparation des données ===
    st.write("### Préparation des statistiques utilisateurs...")

    user_stats = (
        interactions_df.groupby("user_id")
        .agg(
            n_ratings=("rating", "size"),
            mean_rating=("rating", "mean"),
        )
        .reset_index()
    )

    # On définit un "lenient_score" : 5 = indulgent, 1 = sévère
    user_stats["lenient_score"] = user_stats["mean_rating"]

    # === Contrôles interactifs ===
    col1, col2, col3 = st.columns(3)
    with col1:
        log_x = st.checkbox("Axe X logarithmique", value=False)
    with col2:
        x_limit = st.number_input(
            "Limite max de l'axe X", min_value=100, max_value=5000, value=2000, step=100
        )
    with col3:
        jitter = st.slider("Jitter sur Y (dispersion)", 0.0, 0.5, 0.1, 0.05)

    # === Tracé du graphique ===
    df_plot = user_stats.dropna(subset=["n_ratings", "lenient_score"]).copy()
    df_plot = df_plot[df_plot["n_ratings"] > 0]

    if jitter > 0:
        np.random.seed(42)
        df_plot["lenient_score"] += np.random.uniform(
            -jitter, jitter, size=df_plot.shape[0]
        )

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(
        df_plot["n_ratings"],
        df_plot["lenient_score"],
        alpha=0.5,
        s=20,
        c=df_plot["lenient_score"],
        cmap="viridis",
    )

    if log_x:
        ax.set_xscale("log")
    ax.set_xlim(0, x_limit)
    fig.colorbar(scatter, label="Leniency score", ax=ax)
    ax.set_title("Activité vs Sévérité des utilisateurs")
    ax.set_xlabel("Nombre d'avis donnés (n_ratings)")
    ax.set_ylabel("Leniency score (note moyenne)")
    st.pyplot(fig)

    # === Quelques stats globales ===
    st.markdown("---")
    st.write("### 📊 Statistiques globales")
    st.metric("Utilisateurs analysés", f"{len(user_stats):,}")
    st.metric("Note moyenne générale", f"{user_stats['mean_rating'].mean():.2f}/5")
