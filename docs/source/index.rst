Food Analysis WebApp Documentation
===================================

Bienvenue dans la documentation de l'application Food Analysis WebApp.

.. toctree::
   :maxdepth: 2
   :caption: Contenu:

   installation
   usage
   api
   contributing

Introduction
------------

Cette application permet d'analyser les données de recettes et d'interactions 
utilisateurs provenant de Food.com.

Fonctionnalités principales
----------------------------

* Chargement et exploration des données
* Visualisations interactives
* Analyses statistiques
* Interface utilisateur Streamlit

Installation rapide
-------------------

.. code-block:: bash

   git clone https://github.com/VOTRE-USERNAME/food-analysis-webapp.git
   cd food-analysis-webapp
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"

Utilisation
-----------

.. code-block:: bash

   streamlit run src/food_analysis/app.py

API Reference
-------------

.. automodule:: food_analysis.core.data_loader
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: food_analysis.utils.config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: food_analysis.utils.logger
   :members:
   :undoc-members:
   :show-inheritance:

Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`