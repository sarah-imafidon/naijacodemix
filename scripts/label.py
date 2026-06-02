import pandas as pd

# Load feature dataset
df = pd.read_csv("features_tweets.csv")
if "label" in df.columns:
    df = df.drop(columns=["label"])
# ----------------------------
# Binary Labeling Function
# ----------------------------
# 1 → Code-mixed (contains both English + Pidgin)
# 0 → Not code-mixed (mostly English)
def assign_binary_label(row):
    return 1 if row["code_mixed_score"] == 1 else 0

# Apply labeling
df["label"] = df.apply(assign_binary_label, axis=1)

# ----------------------------
# Save labeled dataset
# ----------------------------
df.to_csv("binary_labeled_tweets.csv", index=False)

print("Binary labeling complete ✅")
print(df["label"].value_counts())
print(df.head())