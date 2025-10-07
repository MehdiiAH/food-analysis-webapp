# Base Python
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Créer le dossier de travail
WORKDIR /app

# Installer pip et uv pour gérer les dépendances via pyproject.toml
RUN pip install --upgrade pip
RUN pip install uv  # ou hatch si tu utilises hatch

# Copier pyproject.toml et tout le code
COPY pyproject.toml /app/
COPY src /app/src/

# Installer les dépendances via uv
RUN uv install

# Télécharger modèle spaCy
RUN python -m spacy download en_core_web_sm

# Exposer le port par défaut Streamlit
EXPOSE 8501

# Commande par défaut pour lancer Streamlit
CMD ["streamlit", "run", "src/food_analysis/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
