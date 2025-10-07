# Base Python
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_RUNTIME_ENV=cloud

# Créer le dossier de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir uv

# Copier les fichiers de configuration
COPY pyproject.toml ./

# Copier le code source
COPY src/ ./src/

# Créer les dossiers nécessaires avant l'installation
RUN mkdir -p logs data/raw data/processed

# Installer les dépendances via uv
RUN uv pip install --system -e .

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Commande par défaut
CMD ["streamlit", "run", "src/food_analysis/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]