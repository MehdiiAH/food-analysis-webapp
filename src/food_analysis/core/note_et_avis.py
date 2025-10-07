import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
import seaborn as sns 

#mettre dans github/core


# Import the data and print the first three rows 
recipe = pd.read_csv("recipe/RAW_recipes.csv")
interaction = pd.read_csv("interaction/RAW_interactions.csv")
print(recipe.columns)
print(interaction.columns)

# Calculer la note moyenne et le nombre d'avis par recette
recipe_stats = interaction.groupby('recipe_id').agg(
    avg_rating=('rating', 'mean'),
    n_reviews=('rating', 'count')
).reset_index()

# Paramètres pour la pondération
C = recipe_stats['avg_rating'].mean()  # note moyenne globale
m = 10                                  # nombre minimal d'avis pour fiabilité

# Calculer la note pondérée
recipe_stats['weighted_rating'] = (
    (recipe_stats['n_reviews'] / (recipe_stats['n_reviews'] + m)) * recipe_stats['avg_rating'] +
    (m / (recipe_stats['n_reviews'] + m)) * C
)

# Fusion avec le DataFrame recipe pour récupérer le nom
recipe_stats_with_name = pd.merge(
    recipe_stats,
    recipe[['id', 'name']],  # on garde uniquement id et name
    left_on='recipe_id',
    right_on='id',
    how='left'
)

# Trier par note pondérée décroissante
recipe_stats_with_name = recipe_stats_with_name.sort_values('weighted_rating', ascending=False).reset_index(drop=True)

# Afficher les 10 meilleures recettes avec nom
print(recipe_stats_with_name[['name', 'avg_rating', 'n_reviews', 'weighted_rating']].head(10))
