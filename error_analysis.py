import pandas as pd
import torch
from backend.predict import predict

# ----------------------------
# Load test data
# ----------------------------
test_df = pd.read_csv("data/test.csv")

false_positives = []
false_negatives = []

# ----------------------------
# Loop through test data
# ----------------------------
for _, row in test_df.iterrows():

    text = row["text"]
    true_label = row["label"]

    result = predict(text)
    pred_label = 1 if result["hybrid"]["prediction"] == "Code-Mixed" else 0

    # False Positive
    if pred_label == 1 and true_label == 0:
        false_positives.append(text)

    # False Negative
    if pred_label == 0 and true_label == 1:
        false_negatives.append(text)

# ----------------------------
# Save results
# ----------------------------
pd.DataFrame(false_positives, columns=["False_Positive"]).to_csv("false_positives.csv", index=False)
pd.DataFrame(false_negatives, columns=["False_Negative"]).to_csv("false_negatives.csv", index=False)

print("Error analysis complete ✅")
print(f"False Positives: {len(false_positives)}")
print(f"False Negatives: {len(false_negatives)}")