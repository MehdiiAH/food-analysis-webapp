#!/bin/bash
# Script pour créer automatiquement la structure complète du projet
# Usage: bash create_all_files.sh

echo "🏗️  Création de la structure du projet Food Analysis WebApp"
echo "============================================================"

# Créer la structure de dossiers
echo "📁 Création des dossiers..."
mkdir -p src/food_analysis/{core,utils,pages}
mkdir -p tests/{unit,integration}
mkdir -p docs/source
mkdir -p data/{raw,processed}
mkdir -p .github/workflows
mkdir -p logs

# Créer les fichiers __init__.py
echo "📝 Création des fichiers __init__.py..."
touch src/food_analysis/__init__.py
touch src/food_analysis/core/__init__.py
touch src/food_analysis/utils/__init__.py
touch src/food_analysis/pages/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# Créer les .gitkeep
echo "🔖 Création des .gitkeep..."
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch logs/.gitkeep

# Créer les fichiers Python squelettes
echo "🐍 Création des fichiers Python squelettes..."

# src/food_analysis/app.py
cat > src/food_analysis/app.py << 'EOF'
"""Main Streamlit application.

Ce fichier est le point d'entrée de l'application Streamlit.
À développer par l'équipe.
"""

import streamlit as st


def main() -> None:
    """Point d'entrée principal de l'application."""
    st.set_page_config(
        page_title="Food Analysis WebApp",
        page_icon="🍳",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🍳 Food.com - Analyse de Données")
    st.markdown("**Version:** 0.1.0")
    st.markdown("---")

    st.success("✅ L'application est prête ! Vous pouvez commencer à développer.")
    
    st.info("""
    ### 👨‍💻 À Développer
    
    Cette application est un squelette de base. Voici ce que vous devez faire :
    
    1. **Configuration** : Compléter `src/food_analysis/utils/config.py` et `logger.py`
    2. **Chargement des données** : Implémenter `src/food_analysis/core/data_loader.py`
    3. **Analyse** : Créer `src/food_analysis/core/analyzer.py`
    4. **Pages** : Développer les pages dans `src/food_analysis/pages/`
    5. **Tests** : Écrire des tests dans `tests/`
    
    📚 Consultez le README.md pour plus d'informations !
    """)

    with st.sidebar:
        st.header("🧭 Navigation")
        st.info("Le menu de navigation sera développé ici")
        
        st.markdown("---")
        st.markdown("### 📊 Dataset")
        st.markdown("Food.com Recipes & Interactions")


if __name__ == "__main__":
    main()
EOF

# src/food_analysis/utils/config.py
cat > src/food_analysis/utils/config.py << 'EOF'
"""Configuration module for the application.

Ce module doit contenir :
- Chargement des variables d'environnement (.env)
- Configuration des chemins (data, logs, etc.)
- Constantes de l'application
- Création des dossiers nécessaires

Exemple de structure :
    class Config:
        APP_NAME: str
        DATA_RAW_PATH: Path
        LOGS_PATH: Path
        
        @classmethod
        def create_directories(cls) -> None:
            ...

À DÉVELOPPER PAR L'ÉQUIPE
"""

# TODO: Implémenter la classe Config
# TODO: Utiliser python-dotenv pour charger .env
# TODO: Définir les chemins avec pathlib.Path
EOF

# src/food_analysis/utils/logger.py
cat > src/food_analysis/utils/logger.py << 'EOF'
"""Logging configuration module.

Ce module doit configurer le système de logging de l'application.

Fonctionnalités attendues :
- Configuration des loggers avec différents niveaux (INFO, DEBUG, ERROR)
- Handler console (pour afficher dans le terminal)
- Handler fichier (pour sauvegarder dans logs/)
- Format personnalisé avec timestamp

Exemple de fonction :
    def setup_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
        '''Configure et retourne un logger.'''
        ...

À DÉVELOPPER PAR L'ÉQUIPE
"""

# TODO: Importer logging
# TODO: Créer une fonction setup_logger()
# TODO: Configurer les handlers (console + fichier)
# TODO: Utiliser les configs de config.py
EOF

# src/food_analysis/core/data_loader.py
cat > src/food_analysis/core/data_loader.py << 'EOF'
"""Data loading and preprocessing module.

Ce module doit gérer le chargement des données Food.com.

Classe principale : DataLoader
- Charger RAW_recipes.csv
- Charger RAW_interactions.csv
- Gérer les erreurs (fichier non trouvé, etc.)
- Fournir des méthodes pour accéder aux données
- Logger les opérations

Exemple d'utilisation :
    loader = DataLoader()
    recipes = loader.load_recipes()
    interactions = loader.load_interactions()

À DÉVELOPPER PAR L'ÉQUIPE
"""

# TODO: Créer la classe DataLoader
# TODO: Méthode load_recipes() -> pd.DataFrame
# TODO: Méthode load_interactions() -> pd.DataFrame
# TODO: Gérer les exceptions (FileNotFoundError, etc.)
# TODO: Ajouter du logging
# TODO: Ajouter des docstrings et type hints
EOF

# src/food_analysis/core/analyzer.py
cat > src/food_analysis/core/analyzer.py << 'EOF'
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
EOF

# tests/unit/test_example.py
cat > tests/unit/test_example.py << 'EOF'
"""Example test file.

Ce fichier montre comment écrire des tests avec pytest.
"""

import pytest


def test_example_always_passes() -> None:
    """Test d'exemple qui passe toujours."""
    assert 1 + 1 == 2


def test_example_with_fixture(tmp_path):
    """Test d'exemple utilisant une fixture pytest."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    
    assert test_file.read_text() == "Hello World"


# TODO: Écrire des tests pour DataLoader
# TODO: Écrire des tests pour DataAnalyzer
# TODO: Utiliser des fixtures pour créer des données de test
# TODO: Tester les cas d'erreur (avec pytest.raises)


class TestDataLoader:
    """Tests pour la classe DataLoader."""
    pass


class TestDataAnalyzer:
    """Tests pour la classe DataAnalyzer."""
    pass
EOF

echo ""
echo "✅ Structure créée avec succès !"
echo ""
echo "📝 Prochaines étapes :"
echo "1. Créez manuellement les fichiers de configuration :"
echo "   - pyproject.toml"
echo "   - .gitignore"
echo "   - .env.example"
echo "   - README.md"
echo "   - .github/workflows/ci.yml"
echo "   - docs/source/conf.py"
echo "   - docs/source/index.rst"
echo "   - docs/Makefile"
echo ""
echo "2. Puis lancez :"
echo "   uv venv"
echo "   source .venv/bin/activate"
echo "   uv pip install -e \".[dev]\""
echo ""