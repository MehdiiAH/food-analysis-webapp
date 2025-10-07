import pandas as pd
import spacy


def extract_features(doc, stopwords):
    lemmas = [
        t.lemma_.lower() for t in doc if t.is_alpha and t.text.lower() not in stopwords
    ]
    noun_chunks = [c.text.lower() for c in doc.noun_chunks]
    return lemmas + noun_chunks


def add_token_feature(data_recipe):
    nlp = spacy.load("en_core_web_sm", disable=["ner"])

    stopwords = nlp.Defaults.stop_words

    # DataFrame avec texte
    data_text = data_recipe[["name", "description"]].dropna()

    # Traitement par lots
    tokens_list = []
    for doc in nlp.pipe(data_text["description"].tolist(), batch_size=50, n_process=4):
        tokens_list.append(extract_features(doc, stopwords))

    # Ajouter la colonne tokens au DataFrame original
    data_recipe.loc[data_text.index, "tokens"] = pd.Series(
        tokens_list, index=data_text.index
    )

    # Sauvegarder sous un nouveau nom
    data_recipe.to_csv("data_recipe_with_tokens.csv", index=False)
    print("✅ Fichier 'data_recipe_with_tokens.csv' sauvegardé avec succès !")
