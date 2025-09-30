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
