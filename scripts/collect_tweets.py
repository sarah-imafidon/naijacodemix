# naijasenti_loader.py

from datasets import load_dataset
import pandas as pd

# ----------------------------
# 1️⃣ Load the NaijaSenti Dataset (specifying Nigerian Pidgin)
# ----------------------------
print("Loading NaijaSenti (Nigerian Pidgin) dataset from HuggingFace...")
dataset = load_dataset("mteb/NaijaSenti", "pcm")  # <-- specify pcm for Pidgin

print("Dataset loaded! Available splits:")
print(dataset)

# Convert the training split to pandas DataFrame
train_df = pd.DataFrame(dataset['train'])
print(f"Training split loaded. Total tweets: {len(train_df)}")
print(train_df.head())

# ----------------------------
# 2️⃣ Optional: Filter for Pidgin / Code-mixed Tweets
# ----------------------------
pidgin_keywords = [
    "abeg", "wetin", "no wahala", "dey", "sabi", "oga", "shey", "how far", "na you"
]

def contains_pidgin(text):
    if not isinstance(text, str):
        return False
    return any(word in text.lower() for word in pidgin_keywords)

# Ask user if they want to filter
filter_option = input("Do you want to filter for Pidgin/code-mixed tweets? (y/n): ").lower()
if filter_option == 'y':
    filtered_df = train_df[train_df['text'].apply(contains_pidgin)]
    print(f"Filtered tweets count: {len(filtered_df)}")
else:
    filtered_df = train_df
    print("No filtering applied. Using all tweets.")

# ----------------------------
# 3️⃣ Save the Data to CSV
# ----------------------------
output_file = "filtered_tweets.csv" if filter_option == 'y' else "all_tweets.csv"
filtered_df.to_csv(output_file, index=False)
print(f"Saved dataset to {output_file}")