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
