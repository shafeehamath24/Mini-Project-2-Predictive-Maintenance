# Stage 8 — Build our AI failure-prediction model

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib

# df = pd.read_csv("processed_machine_data.csv")

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / "processed_machine_data.csv")

X = df.drop(columns=[
    "Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"
])

y = df["Machine failure"]

X = pd.get_dummies(X, columns=["Type"])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42 
)

model.fit(X_train, y_train)

# predictions = model.predict(X_test)

probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.30).astype(int)

print("AI ENGINEERING RESULTS")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print("Precision:", round(precision_score(y_test, predictions, zero_division=0), 4))
print("Recall:", round(recall_score(y_test, predictions, zero_division=0), 4))
print("F1-score:", round(f1_score(y_test, predictions, zero_division=0), 4))
print("\nConfusion matrix:")
print(confusion_matrix(y_test, predictions))
print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

# joblib.dump({"model": model, "features": list(X.columns)}, "failure_model.pkl")


# joblib.dump(
#     {"model": model, "features": list(X.columns)},
#     BASE_DIR / "backend" / "failure_model.pkl"
# )

joblib.dump(
    {
        "model": model,
        "features": list(X.columns),
        "threshold": 0.30
    },
    BASE_DIR / "backend" / "failure_model.pkl"
)



print("Saved trained model: failure_model.pkl")


# Testing — Find a historical record predicted as a machine failure 
# Next step — Add a failure-case finder

test_data = X_test.copy()
test_data["Actual failure"] = y_test
test_data["Predicted failure"] = predictions

failure_cases = test_data[test_data["Predicted failure"] == 1]

print("\nSAMPLE FAILURE PREDICTIONS")

if len(failure_cases) > 0:
    print(failure_cases.head(5))
else:
    print("No failure predictions found in the test data.")
