"""Module d'analyse des données Food.com.

Version simple pour démarrer. L'équipe pourra ajouter plus de méthodes.
"""

from typing import Dict, Any
import pandas as pd


class DataAnalyzer:
    """Classe pour analyser les données de recettes et interactions."""

    def __init__(
        self,
        recipes: pd.DataFrame,
        interactions: pd.DataFrame
    ) -> None:
        """Initialise l'analyseur avec les données."""
        self.recipes = recipes
        self.interactions = interactions

    def get_basic_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques de base sur les données."""
        stats = {
            'total_recipes': len(self.recipes),
            'total_interactions': len(self.interactions),
            'total_users': self.interactions['user_id'].nunique() if 'user_id' in self.interactions.columns else 0,
        }
        return stats

    def get_top_recipes(self, n: int = 10) -> pd.DataFrame:
        """Retourne les N recettes avec le plus d'interactions."""
        if self.interactions.empty:
            return pd.DataFrame()
        
        recipe_counts = self.interactions['recipe_id'].value_counts().head(n)
        top_recipes = self.recipes[self.recipes['id'].isin(recipe_counts.index)]
        return top_recipes

    def get_average_rating(self) -> float:
        """Calcule la note moyenne de toutes les recettes."""
        if 'rating' not in self.interactions.columns:
            return 0.0
        
        valid_ratings = self.interactions[self.interactions['rating'] > 0]['rating']
        if len(valid_ratings) == 0:
            return 0.0
        
        return float(valid_ratings.mean())


# TODO pour l'équipe : Ajouter d'autres méthodes d'analyse
