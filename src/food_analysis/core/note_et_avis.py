import pandas as pd

# mettre dans github/core


# # Import the data and print the first three rows
# recipe = pd.read_csv("recipe/RAW_recipes.csv")
# interaction = pd.read_csv("interaction/RAW_interactions.csv")
# print(recipe.columns)
# print(interaction.columns)

# # Calculer la note moyenne et le nombre d'avis par recette
# recipe_stats = interaction.groupby('recipe_id').agg(
#     avg_rating=('rating', 'mean'),
#     n_reviews=('rating', 'count')
# ).reset_index()

# # Paramètres pour la pondération
# C = recipe_stats['avg_rating'].mean()  # note moyenne globale
# m = 10                                  # nombre minimal d'avis pour fiabilité

# # Calculer la note pondérée
# recipe_stats['weighted_rating'] = (
#     (recipe_stats['n_reviews'] / (recipe_stats['n_reviews'] + m)) * recipe_stats['avg_rating'] +
#     (m / (recipe_stats['n_reviews'] + m)) * C
# )

# # Fusion avec le DataFrame recipe pour récupérer le nom
# recipe_stats_with_name = pd.merge(
#     recipe_stats,
#     recipe[['id', 'name']],  # on garde uniquement id et name
#     left_on='recipe_id',
#     right_on='id',
#     how='left'
# )

# # Trier par note pondérée décroissante
# recipe_stats_with_name = recipe_stats_with_name.sort_values('weighted_rating', ascending=False).reset_index(drop=True)

# # Afficher les 10 meilleures recettes avec nom
# print(recipe_stats_with_name[['name', 'avg_rating', 'n_reviews', 'weighted_rating']].head(10))


# Fonctions pour charger les données


def load_recipes(path: str = "recipe/RAW_recipes.csv") -> pd.DataFrame:
    """
    Charge les recettes depuis un fichier CSV.

    Args:
        path (str): chemin vers le fichier CSV

    Returns:
        pd.DataFrame: DataFrame contenant les recettes
    """
    return pd.read_csv(path)


def load_interactions(path: str = "interaction/RAW_interactions.csv") -> pd.DataFrame:
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
