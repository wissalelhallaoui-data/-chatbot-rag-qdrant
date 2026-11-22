# Chatbot RAG pour les règlements universitaires

Assistant qui répond aux questions des étudiants sur les règlements universitaires, à partir des documents officiels.

> Projet académique.

## Problématique

Les règlements universitaires sont longs et difficiles à parcourir. Ce projet permet de poser une question en langage naturel et d'obtenir une réponse fondée sur les articles du règlement, avec l'indication des sources.

Réalisé dans le cadre de mon Master en Ingénierie des Systèmes Intelligents.

## Architecture

```
Documents (.txt)
      │  découpage par article
      ▼
Passages ──► embeddings (bge-m3 via Ollama, 1024 dimensions)
      │
      ▼
Base vectorielle Qdrant Cloud (distance cosinus)
      ▲
Question ──► embedding ──► recherche des 3 passages les plus proches
                                   │
                                   ▼
                      Llama 3.2 3B (via Ollama, en local) ──► réponse + sources
```

## Fonctionnement

1. **Indexation** (`scripts/index_txts.py`) : chaque document texte est découpé **par article** (« Article N : »), ce qui garde chaque règle entière dans un seul passage. Les passages sont transformés en vecteurs avec `bge-m3`, un modèle d'embedding multilingue, puis stockés dans **Qdrant Cloud** avec leurs métadonnées (fichier source, numéro d'article).
2. **Recherche** : la question est transformée en vecteur avec le même modèle, et Qdrant renvoie les 3 passages les plus proches par similarité cosinus.
3. **Génération** (`scripts/chatbot.py`) : les passages sont fournis comme contexte à Llama 3.2 3B, qui répond uniquement à partir de ce contexte. Si l'information est absente, l'assistant le dit. La réponse est suivie des sources (fichier et article).

## Exemple d'utilisation

**Question :** [une vraie question que tu as testée]

**Réponse :** [la réponse obtenue, copiée telle quelle]

**Sources :** [fichier - article, tels qu'affichés]

## Exécution

Les embeddings et le LLM tournent en local sur la machine via Ollama. La base vectorielle est hébergée sur Qdrant Cloud : une connexion internet est donc nécessaire pour la recherche.

## Technologies

Python, Ollama (Llama 3.2 3B, bge-m3), Qdrant Cloud, python-dotenv

## Installation et utilisation

**Prérequis :** Python 3.10 ou plus récent, [Ollama](https://ollama.com) installé et lancé, et un compte Qdrant Cloud.

```bash
git clone https://github.com/wissalelhallaoui-data/chatbot-rag-universitaire.git
cd chatbot-rag-universitaire
pip install -r requirements.txt

# Télécharger les modèles
ollama pull bge-m3
ollama pull llama3.2:3b
```

Crée un fichier `.env` à la racine du projet avec tes identifiants Qdrant Cloud :

```
QDRANT_URL=https://ton-cluster.qdrant.io
QDRANT_API_KEY=ta_cle_qdrant_cloud
```

Puis :

```bash
# 1. Indexer les documents (une seule fois, ou après modification des documents)
python scripts/index_txts.py

# 2. Lancer le chatbot en ligne de commande
python scripts/chatbot.py
```

## Ajouter ses propres documents

Place des fichiers `.txt` dans le dossier `documents/`, puis relance `python scripts/index_txts.py`. Le découpage attend des articles de la forme `Article 1 : ...`.



## Auteure

**Wissal EL HALLAOUI**, étudiante en M2 Ingénierie des Systèmes Intelligents
[LinkedIn](https://www.linkedin.com/in/wissal-el-hallaoui-a8b9bb29a)
