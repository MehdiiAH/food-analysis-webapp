# 🍳 Food.com Recipes - Application d'Analyse de Données

Application web Streamlit pour l'analyse des recettes et interactions utilisateurs du dataset Food.com.

## 📋 Description du Projet

Ce projet est une application web d'analyse de données développée avec Streamlit, permettant d'explorer et d'analyser les recettes de cuisine et les interactions utilisateurs provenant de Food.com.

### Fonctionnalités

- 📊 Visualisation interactive des données
- 🔍 Analyse exploratoire des recettes
- 👥 Analyse des interactions utilisateurs

## 🚀 Installation

### Prérequis

- Python 3.11 ou supérieur
- [uv](https://github.com/astral-sh/uv) installé

### Configuration de l'environnement

```bash
# Cloner le dépôt
git clone https://github.com/MehdiiAH/food-analysis-webapp.git
cd food-analysis-webapp

# Créer l'environnement virtuel et installer les dépendances
uv venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
uv pip install -e ".[dev]"

# Copier le fichier d'environnement
cp .env.example .env
```

## 💻 Utilisation

### Lancer l'application

```bash
streamlit run src/food_analysis/app.py
```

L'application sera accessible à l'adresse : http://localhost:8501

### Développement

```bash
# Lancer les tests
pytest

# Vérifier la couverture de code
pytest --cov=src/food_analysis --cov-report=html

# Linter et formatter le code
ruff check src/ tests/
ruff format src/ tests/

# Vérification des types
mypy src/

# Générer la documentation
cd docs
make html
```

## 📁 Structure du Projet

```
food-analysis-webapp/
├── src/food_analysis/     # Code source
│   ├── core/             # Logique métier
│   ├── utils/            # Utilitaires
│   └── pages/            # Pages Streamlit
├── tests/                # Tests unitaires et d'intégration
├── data/                 # Données (non versionnées)
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD GitHub Actions
```

## 🧪 Tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests d'intégration uniquement
pytest tests/integration/

# Avec couverture
pytest --cov
```

## 🤝 Contribution

### Workflow Git pour l'équipe

1. **Créer une branche pour votre fonctionnalité**

   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```

2. **Faire vos modifications et commits**

   ```bash
   git add .
   git commit -m "Description claire des changements"
   ```

3. **Pousser votre branche**

   ```bash
   git push origin feature/nom-de-la-fonctionnalite
   ```

4. **Créer une Pull Request sur GitHub**

5. **Après validation, merger dans main**

### Conventions

- Suivre PEP 8
- Ajouter des tests pour les nouvelles fonctionnalités
- Documenter le code (docstrings)
- Utiliser le type hinting

## 👥 Équipe

- AIT HAMMA Mehdi
- ELWARADI Reda
- HAMON Rémi
- HORDOIR Stéphane
- NIOL Julien

## Code coverage

[![codecov](https://codecov.io/gh/MehdiiAH/food-analysis-webapp/branch/main/graph/badge.svg?token=)](https://codecov.io/gh/MehdiiAH/food-analysis-webapp)

## 📄 Licence

MIT License
