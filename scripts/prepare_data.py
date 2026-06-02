import pandas as pd
from sklearn.model_selection import train_test_split

# ----------------------------
# Load dataset with features + ORIGINAL labels
# ----------------------------
df = pd.read_csv("../data/features_tweets.csv")

# ----------------------------
# Convert original labels to binary
# 1 → Code-mixed (assuming original label 2 = code-mixed)
# 0 → Not code-mixed (labels 0 and 1)
def relabel(row):
    if row["pidgin_ratio"] > 0.2:
        return 1
    if row["switch_count"] > 0:
        return 1
    return 0

df["label"] = df.apply(relabel, axis=1)

# ----------------------------
# Keep only needed columns
# ----------------------------
df = df[["clean_text", "label"]]

# ----------------------------
# Remove missing values
# ----------------------------
df = df.dropna()

# ----------------------------
# Check label distribution (VERY IMPORTANT)
# ----------------------------
print("Label distribution:")
print(df["label"].value_counts())

# ----------------------------
# Train-test split (stratified)
# ----------------------------
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df["clean_text"],
    df["label"],
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

# ----------------------------
# Save splits
# ----------------------------
train_df = pd.DataFrame({
    "text": train_texts,
    "label": train_labels
})

test_df = pd.DataFrame({
    "text": test_texts,
    "label": test_labels
})

train_df.to_csv("../data/train.csv", index=False)
test_df.to_csv("../data/test.csv", index=False)

print("\nData preparation complete ✅")
print("\nSample training data:")
print(train_df.head())