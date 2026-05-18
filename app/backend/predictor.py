import joblib
import json
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
GENES_PATH = MODEL_DIR / "selected_genes.json"


class Predictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.selected_genes = None
        self.load_artifacts()

    def load_artifacts(self):
        """Charge le modèle, le scaler et les gènes sélectionnés."""
        try:
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            with open(GENES_PATH, "r") as f:
                self.selected_genes = json.load(f)
            print("✅ Modèle chargé avec succès.")
        except Exception as e:
            print(f"⚠️ Erreur chargement modèle : {e}")

    def is_ready(self):
        """Vérifie si tous les artefacts sont chargés."""
        return (
            self.model is not None
            and self.scaler is not None
            and self.selected_genes is not None
        )

    def get_genes(self):
        """Retourne la liste des gènes sélectionnés."""
        return self.selected_genes

    def predict(self, data: dict):
        """
        Effectue une prédiction à partir d'un dictionnaire {gene: valeur}.
        Retourne (prediction, confidence).
        """
        # 1. Vérifier les gènes manquants
        for gene in self.selected_genes:
            if gene not in data:
                raise ValueError(f"Gène manquant: {gene}")

        # 2. Réordonner selon l'ordre exact du modèle
        features = np.array([[data[gene] for gene in self.selected_genes]])

        # 3. Transformer avec scaler
        features_scaled = self.scaler.transform(features)

        # 4. Prédire
        pred_class = int(self.model.predict(features_scaled)[0])
        prob = self.model.predict_proba(features_scaled)[0]

        # LabelEncoder alphabétique : Abnormal=0, Normal=1
        le_map = {0: "Abnormal", 1: "Normal"}
        prediction = le_map.get(pred_class, str(pred_class))
        confidence = float(np.max(prob))

        return prediction, confidence


# Instance globale
predictor = Predictor()
