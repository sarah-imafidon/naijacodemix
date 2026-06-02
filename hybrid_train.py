import pandas as pd
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# ----------------------------
# Load Features Dataset (WITH ORIGINAL LABELS)
# ----------------------------
df = pd.read_csv("data/features_tweets.csv")
df = df.dropna()

def relabel(row):
    if row["pidgin_ratio"] > 0.2:
        return 1
    if row["switch_count"] > 0:
        return 1
    return 0

df["label"] = df.apply(relabel, axis=1)

print("Label distribution:")
print(df["label"].value_counts())

# ----------------------------
# Feature Columns (NO leakage)
# ----------------------------
feature_cols = [
    "contains_pidgin",
    "pidgin_word_count",
    "particle_count",
    "has_reduplication",
    "switch_count",
    "english_ratio"
]

# ----------------------------
# Train/Test Split
# ----------------------------
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

# ----------------------------
# Normalize Features
# ----------------------------
scaler = StandardScaler()
train_features = scaler.fit_transform(train_df[feature_cols])
test_features = scaler.transform(test_df[feature_cols])
# ✅ SAVE SCALER HERE
joblib.dump(scaler, "scaler.pkl")

# Labels
train_labels = torch.tensor(train_df["label"].values, dtype=torch.long)
test_labels = torch.tensor(test_df["label"].values, dtype=torch.long)

# ----------------------------
# Load Baseline AfroXLMR
# ----------------------------
model_name = "baseline_afroxlm_model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
transformer = AutoModel.from_pretrained(model_name)

# Freeze transformer (CPU-friendly)
for param in transformer.parameters():
    param.requires_grad = False

# ----------------------------
# Custom Dataset
# ----------------------------
class HybridTweetDataset(Dataset):
    def __init__(self, texts, features, labels):
        self.texts = texts.reset_index(drop=True)
        self.features = torch.tensor(features, dtype=torch.float32)
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = tokenizer(
            self.texts[idx],
            truncation=True,
            padding='max_length',
            max_length=64,
            return_tensors="pt"
        )
        encoding = {k: v.squeeze(0) for k, v in encoding.items()}
        return encoding, self.features[idx], self.labels[idx]

train_dataset = HybridTweetDataset(train_df["clean_text"], train_features, train_labels)
test_dataset = HybridTweetDataset(test_df["clean_text"], test_features, test_labels)

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=8)

# ----------------------------
# Hybrid Model
# ----------------------------
class HybridClassifier(nn.Module):
    def __init__(self, transformer, feature_dim, hidden_dim=32, num_labels=2):
        super(HybridClassifier, self).__init__()
        self.transformer = transformer

        cls_dim = transformer.config.hidden_size
        self.fc1 = nn.Linear(cls_dim + feature_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_labels)

    def forward(self, input_ids, attention_mask, features):
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        combined = torch.cat([cls_embedding, features], dim=1)
        x = self.fc1(combined)
        x = self.relu(x)
        logits = self.fc2(x)
        return logits

feature_dim = train_features.shape[1]
model = HybridClassifier(transformer, feature_dim)

# ----------------------------
# Optimizer & Loss
# ----------------------------
optimizer = torch.optim.Adam(model.parameters(), lr=2e-4)
from torch.nn import CrossEntropyLoss
class_weights = torch.tensor([1.0, 1.2])  

criterion = CrossEntropyLoss(weight=class_weights)

# ----------------------------
# Training Loop
# ----------------------------
device = torch.device("cpu")
model.to(device)

num_epochs = 2
for epoch in range(num_epochs):
    model.train()
    total_loss = 0

    for batch in train_loader:
        encoding, features, labels = batch

        input_ids = encoding["input_ids"].to(device)
        attention_mask = encoding["attention_mask"].to(device)
        features = features.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        logits = model(input_ids=input_ids, attention_mask=attention_mask, features=features)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{num_epochs} | Loss: {total_loss/len(train_loader):.4f}")

# ----------------------------
# Evaluation
# ----------------------------
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for batch in test_loader:
        encoding, features, labels = batch

        input_ids = encoding["input_ids"].to(device)
        attention_mask = encoding["attention_mask"].to(device)
        features = features.to(device)
        labels = labels.to(device)

        logits = model(input_ids=input_ids, attention_mask=attention_mask, features=features)
        preds = torch.argmax(logits, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# Convert to metrics
accuracy = accuracy_score(all_labels, all_preds)
precision, recall, f1, _ = precision_recall_fscore_support(
    all_labels, all_preds, average="binary"
)

print(f"\nHybrid Model Results:")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

# Extra (very useful for your report)
print("\nClassification Report:")
print(classification_report(all_labels, all_preds))

print("\nConfusion Matrix:")
print(confusion_matrix(all_labels, all_preds))

# ----------------------------
# Save Hybrid Model
# ----------------------------
torch.save(model.state_dict(), "hybrid_afroxlm_model.pt")
print("Hybrid model saved ✅")