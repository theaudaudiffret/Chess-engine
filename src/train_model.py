import argparse
import json
import os


import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models

from utils_ai import split_dims


def load_data(data_path):
    dfs = []
    for filename in os.listdir(data_path):
        if filename.endswith('.json'):
            filepath = os.path.join(data_path, filename)
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        df = pd.DataFrame(data)
                        df = df.iloc[:-6]
                        dfs.append(df)
                    except json.JSONDecodeError as e:
                        print(f"Erreur de décodage JSON dans le fichier {filepath}: {e}")
                        continue
    return pd.concat(dfs, ignore_index=True)

def preprocess_data(train_df):
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    train_df = train_df.drop(train_df[train_df['position'].apply(lambda x: isinstance(x, float))].index)
    train_df = train_df.drop(train_df[~train_df['evaluation'].apply(lambda x: isinstance(x, (float, int)))].index)
    return train_test_split(train_df, test_size=0.2, random_state=42)

def build_model(input_shape):
    model = models.Sequential()
    model.add(layers.Input(shape=input_shape))
    model.add(layers.Conv2D(64, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.Conv2D(256, (1, 1), activation='relu'))
    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

def train_model(data_path, epochs=10, batch_size=64, model_save_path = 'models/mps.keras'):
    # Charger et prétraiter les données
    train_df = load_data(data_path)
    train_df, val_df = preprocess_data(train_df)

    X_train = np.stack(train_df['position'].apply(split_dims))
    y_train = train_df['evaluation']
    X_val = np.stack(val_df['position'].apply(split_dims))
    y_val = val_df['evaluation']

    # Construire et entraîner le modèle
    model = build_model(input_shape=(14, 8, 8))
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )

    # Évaluer le modèle
    accuracy = model.evaluate(X_val, y_val)
    print(f"Accuracy of the training: {accuracy}")

    # Sauvegarder le modèle
    model.save(model_save_path)

    return model, history

    
if __name__ == '__main__':
    # Création du parser d'arguments
    parser = argparse.ArgumentParser(description="Entraîner un modèle.")
    parser.add_argument('--data_path', type=str, required=True, help='Chemin vers les données')
    parser.add_argument('--epochs', type=int, required=True, help='Nombre d\'epochs')
    parser.add_argument('--batch_size', type=int, required=True, help='Taille du batch')
    parser.add_argument('--model_save_path', type=str, required=True, help='Chemin pour sauvegarder le modèle')

    # Récupérer les arguments passés en ligne de commande
    args = parser.parse_args()

    # Appel de la fonction avec les arguments passés
    trained_model, training_history = train_model(
        data_path=args.data_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        model_save_path=args.model_save_path
    )