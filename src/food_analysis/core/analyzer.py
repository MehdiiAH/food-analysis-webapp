"""Module d'analyse des données Food.com.

Version simple pour démarrer. L'équipe pourra ajouter plus de méthodes.
"""

import numpy as np
import pandas as pd

# Fonction pour calculer les statistiques des recettes


def compute_recipe_stats(
    recipe_df: pd.DataFrame, interaction_df: pd.DataFrame, m: int = 10
) -> pd.DataFrame:
    """
    Calcule la note moyenne, le nombre d'avis et la note pondérée pour chaque recette.

    Args:
        recipe_df (pd.DataFrame): DataFrame des recettes
        interaction_df (pd.DataFrame): DataFrame des interactions
        m (int): Nombre minimal d'avis pour la pondération

    Returns:
        pd.DataFrame: DataFrame avec id, nom, avg_rating, n_reviews et weighted_rating
    """
    # Calculer la note moyenne et le nombre d'avis par recette
    recipe_stats = (
        interaction_df.groupby("recipe_id")
        .agg(avg_rating=("rating", "mean"), n_reviews=("rating", "count"))
        .reset_index()
    )

    # Note moyenne globale
    C = recipe_stats["avg_rating"].mean()

    # Calcul de la note pondérée
    recipe_stats["weighted_rating"] = (
        recipe_stats["n_reviews"] / (recipe_stats["n_reviews"] + m)
    ) * recipe_stats["avg_rating"] + (m / (recipe_stats["n_reviews"] + m)) * C

    # Fusion avec le DataFrame recipe pour récupérer le nom
    recipe_stats_with_name = pd.merge(
        recipe_stats,
        recipe_df[["id", "name"]],
        left_on="recipe_id",
        right_on="id",
        how="left",
    )

    # Trier par note pondérée décroissante
    recipe_stats_with_name = recipe_stats_with_name.sort_values(
        "weighted_rating", ascending=False
    ).reset_index(drop=True)

    return recipe_stats_with_name[
        ["name", "avg_rating", "n_reviews", "weighted_rating"]
    ]


def recipe_reviews(recipe_id: int, interaction_df: pd.DataFrame) -> pd.DataFrame:
    """
    Récupère les avis pour une recette donnée.

    Args:
        recipe_id (int): ID de la recette
        interaction_df (pd.DataFrame): DataFrame des interactions

    Returns:
        pd.DataFrame: DataFrame contenant les avis pour la recette
    """
    return (
        interaction_df[interaction_df["recipe_id"] == recipe_id][
            ["user_id", "rating", "date", "review"]
        ]
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
    )


def compute_user_stats(
    recipe_df: pd.DataFrame, interaction_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcule les statistiques utilisateur : activité, notes données, leniency score,
    et caractéristiques des recettes testées.

    Args:
        recipe_df (pd.DataFrame): DataFrame des recettes
        interaction_df (pd.DataFrame): DataFrame des interactions

    Returns:
        pd.DataFrame: DataFrame des features utilisateur
    """
    df = interaction_df.dropna(subset=["user_id", "recipe_id", "rating"]).copy()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Features de base
    user_stats = (
        df.groupby("user_id")
        .agg(
            n_ratings=("rating", "count"),
            avg_rating_given=("rating", "mean"),
            std_rating_given=("rating", "std"),
        )
        .reset_index()
    )

    # Nombre de jours actifs
    if "date" in df.columns:
        user_time = df.groupby('user_id')['date'].agg(['min','max'])
        user_stats["n_days_active"] = (user_time["max"] - user_time["min"]).dt.days + 1
    else:
        user_stats["n_days_active"] = np.nan

    # Préparer recettes pour features
    recipes = recipe_df.copy()
    recipes["n_ingredients"] = recipes["ingredients"].apply(
        lambda x: len(eval(x)) if pd.notnull(x) else np.nan
    )
    recipes["n_steps"] = recipes["steps"].apply(
        lambda x: len(eval(x)) if pd.notnull(x) else np.nan
    )

    # Merge pour features basées sur recettes
    merged = df.merge(
        recipes[["id", "minutes", "n_ingredients", "n_steps"]],
        left_on="recipe_id",
        right_on="id",
        how="left",
    )

    user_recipe_stats = (
        merged.groupby("user_id")
        .agg(
            avg_recipe_time=("minutes", "mean"),
            avg_ingredients=("n_ingredients", "mean"),
            avg_steps=("n_steps", "mean"),
        )
        .reset_index()
    )

    user_stats = user_stats.merge(user_recipe_stats, on="user_id", how="left")

    # Leniency score
    global_mean = df["rating"].mean()
    user_stats["lenient_score"] = user_stats["avg_rating_given"] - global_mean

    return user_stats
