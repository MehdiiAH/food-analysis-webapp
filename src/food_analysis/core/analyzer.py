"""Module d'analyse des données Food.com.

Version simple pour démarrer. L'équipe pourra ajouter plus de méthodes.
"""

# Ajout logging et exceptions
import logging
from logging.handlers import RotatingFileHandler

import pandas as pd

# Messages de log à différents niveaux
logging.debug("Ceci est un message de niveau DEBUG")
logging.info("Ceci est un message de niveau INFO")
logging.warning("Ceci est un message de niveau WARNING")
logging.error("Ceci est un message de niveau ERROR")
logging.critical("Ceci est un message de niveau CRITICAL")

# Création d'un logger pour ce module
logger = logging.getLogger(__name__)

# Définir le niveau de log sur INFO
logger.setLevel(logging.INFO)

# Création d'un handler permettant la rotation des logs, avec format compréhensible

file_handler = RotatingFileHandler(
    "analyzer.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
handler_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(handler_format)

console_handler = logging.StreamHandler()
console_handler.setFormatter(handler_format)
console_handler.setLevel(logging.INFO)

# Éviter d'ajouter plusieurs handlers si le module est importé plusieurs fois
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


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

    Raises:
        EmptyDataError si l'un des DataFrames est vide.
    """

    try:
        interaction_df.empty or recipe_df.empty
    except pd.errors.EmptyDataError:
        logger.warning("Attention: l'un des DataFrames est vide.")

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

    Raises:
        EmptyDataError si le DataFrame des interactions est vide.
    """
    try:
        interaction_df.empty
    except pd.errors.EmptyDataError:
        logger.warning("Attention: le DataFrame des interactions est vide.")
    return (
        interaction_df[interaction_df["recipe_id"] == recipe_id][
            ["user_id", "rating", "date", "review"]
        ]
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
    )
