import pandas as pd
import re

# Load your dataset
df = pd.read_csv("filtered_tweets.csv")

# Cleaning function
def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    text = text.lower()  # lowercase
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"@\w+", "", text)  # remove mentions
    text = re.sub(r"#\w+", "", text)  # remove hashtags
    text = re.sub(r"[^a-z\s]", "", text)  # remove punctuation & numbers
    text = re.sub(r"\s+", " ", text).strip()  # remove extra spaces
    
    return text

# Apply cleaning
df['clean_text'] = df['text'].apply(clean_text)

# Save cleaned version
df.to_csv("cleaned_tweets.csv", index=False)

print("Cleaning complete. Saved as cleaned_tweets.csv")
print(df[['text', 'clean_text']].head())