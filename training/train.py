import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import json
import os

print("🚀 Démarrage de l'entraînement...")

# 1. Charger le dataset
df = pd.read_csv('/app/data/colon_cancer_dataset.csv')
X = df.drop("Class", axis=1)
y = df["Class"]

# 2. Encoder les labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)  # Abnormal=0, Normal=1
print(f"📋 Classes : {list(le.classes_)}")

# 3. Standardiser TOUT le dataset
scaler_full = StandardScaler()
X_scaled_full = scaler_full.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled_full, columns=X.columns)

# 4. Forward Feature Selection (Top 10)
print("🧬 Début du Forward Feature Selection...")
selected_features = []
for i in range(10):
    best_acc = 0
    best_feature = None

    for feature in X_scaled_df.columns:
        if feature not in selected_features:
            features_to_test = selected_features + [feature]
            X_subset = X_scaled_df[features_to_test]

            X_train, X_test, y_train, y_test = train_test_split(
                X_subset, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )

            model_temp = LogisticRegression(max_iter=1000)
            model_temp.fit(X_train, y_train)
            acc = accuracy_score(y_test, model_temp.predict(X_test))

            if acc > best_acc:
                best_acc = acc
                best_feature = feature

    selected_features.append(best_feature)
    print(f"   -> Étape {i+1} : {best_feature} ajouté (Accuracy: {best_acc:.4f})")

print(f"\n🏆 Top 10 gènes sélectionnés : {selected_features}")

# 5. Garder Top 6
top_6_genes = selected_features[:6]
print(f"🎯 Top 6 gènes finaux : {top_6_genes}")

# 6. Entraîner le modèle final sur les Top 6
X_final = X[top_6_genes]
X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
    X_final, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

final_scaler = StandardScaler()
X_train_f_scaled = final_scaler.fit_transform(X_train_f)
X_test_f_scaled = final_scaler.transform(X_test_f)

final_model = LogisticRegression(max_iter=1000)
final_model.fit(X_train_f_scaled, y_train_f)

# 7. Évaluation
print("\n📊 Évaluation finale:")
print(f"Train Accuracy: {final_model.score(X_train_f_scaled, y_train_f):.4f}")
print(f"Test Accuracy:  {final_model.score(X_test_f_scaled, y_test_f):.4f}")

y_pred = final_model.predict(X_test_f_scaled)

print("\nClassification Report (Test):")
print(classification_report(y_test_f, y_pred, target_names=le.classes_))

print("Confusion Matrix (Test):")
print(confusion_matrix(y_test_f, y_pred))

# 8. Sauvegarder les artefacts
os.makedirs("/app/model", exist_ok=True)
joblib.dump(final_model, "/app/model/model.pkl")
joblib.dump(final_scaler, "/app/model/scaler.pkl")

with open("/app/model/selected_genes.json", "w") as f:
    json.dump(top_6_genes, f)

print("\n✅ Modèle, Scaler et Gènes sauvegardés avec succès dans /app/model/")
