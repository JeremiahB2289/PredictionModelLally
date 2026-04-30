import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("../../data/training_data.csv")

# Features + label
X = df.drop(columns=["label"])
y = df["label"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=10,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

print(f"Accuracy: {acc:.3f}")
print(classification_report(y_test, preds))

# Save model
with open("../models/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as model.pkl")