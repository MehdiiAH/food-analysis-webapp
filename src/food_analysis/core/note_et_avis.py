import pandas as pd

# Fonctions pour charger les données


def load_recipes(path: str = "../../../data/raw/RAW_recipes.csv") -> pd.DataFrame:
    """
    Charge les recettes depuis un fichier CSV.

    Args:
        path (str): chemin vers le fichier CSV

    Returns:
        pd.DataFrame: DataFrame contenant les recettes
    """
    return pd.read_csv(path)


def load_interactions(
    path: str = "../../../data/raw/RAW_interactions.csv",
) -> pd.DataFrame:
    """
    Charge les interactions (avis) depuis un fichier CSV.

    Args:
        path (str): chemin vers le fichier CSV

    Returns:
        pd.DataFrame: DataFrame contenant les interactions
    """
    return pd.read_csv(path)


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


def plot_rating_distribution(interaction_df: pd.DataFrame, recipe_id: int) -> None:
    """
    Affiche la distribution des notes pour une recette spécifique.
    """
    import matplotlib.pyplot as plt

    ratings = interaction_df.loc[interaction_df["recipe_id"] == recipe_id, "rating"]
    plt.hist(ratings, bins=6, edgecolor="black")
    plt.xlim(-0.25, None)
    plt.title(f"Distribution des notes pour la recette {recipe_id}")
    plt.xlabel("Note")
    plt.ylabel("Nombre d'avis")
    # plt.xticks([])
    plt.show()
    
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
