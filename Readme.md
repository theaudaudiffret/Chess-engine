# Projet de Développement d'un Moteur d'Échecs par IA

## Objectif du Projet

L'objectif est de développer une IA capable de rivaliser avec un adversaire humain de 1000 elos. Le projet suit une approche évolutive :

1. Commencer par une approche rule-based (initialement insatisfaisante pour des situations complexes)
2. Passer à un apprentissage supervisé avec un Réseau de Neurones Convolutif (CNN)
3. Générer des parties d'échecs avec Stockfish impliquant des joueurs de très haut niveau (elo > 3000)
4. Entraîner un réseau de neurones pour évaluer les plateaux d'échecs
5. Créer un bot d'échecs avec une profondeur de calcul paramétrable (recommandation : profondeur 0 ou 1 initialement)

## Structure du Repository

### Répertoires
Créer les répertoires data et models 
- `data/` : Jeux de données pour l'entraînement de l'IA
- `models/` : Modèles d'IA entraînés
- `src/` : Scripts source du projet
  - `config/` : Emplacement du fichier .env (path vers Stockfish)
  - `generate_data.py` : Script de génération des données d'entraînement
  - `train_model.py` : Script d'entraînement du modèle
  - `utils_ai.py` : Scripts pour le moteur IA
  - `utils_rule_based.py` : Scripts pour le moteur rule-based

### Fichiers Principaux

- `.gitignore` : Configuration Git
- `play_against_ai.ipynb` : Notebook pour jouer contre l'IA entraînée par CNN
- `play_against_basic_ai.ipynb` : Notebook pour jouer contre une IA basique
- `requirements.txt` : Dépendances Python

## Prise en Main

### Installation

1. Se placer dans le répertoire `chess-engine`
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Installer Stockfish sur votre machine
4. Configurer le chemin de Stockfish dans `src/config/.env`

### Modes de Jeu

#### Mode 1 : Contre l'Engine Rule-Based
- Jouer directement dans `play_against_basic_engine.ipynb`

#### Mode 2 : Contre l'Engine Entraîné

1. Créer le dataset d'entraînement :
   ```bash
   python src/generate_dataset.py \
     --numGames 50 \
     --maxMoves 400 \
     --elo 1800 \
     --evaluatorElo 3000 \
     --depth 3 \
     --threads 4 \
     --minTime 20
   ```

2. Entraîner le modèle :
   ```bash
   python src/train_model.py \
     --data_path "data" \
     --epochs 10 \
     --batch_size 64 \
     --model_save_path "models/mps.keras"
   ```

3. Jouer contre l'IA dans `play_against_ai.ipynb`
