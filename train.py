import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ----------------------------
# Load Data
# ----------------------------
train_df = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

# ----------------------------
# Load AfroXLMR
# ----------------------------
model_name = "Davlan/afro-xlmr-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# ----------------------------
# Freeze Base Layers for CPU (except last layer)
# ----------------------------
for param in model.base_model.parameters():
    param.requires_grad = False

# Unfreeze LAST transformer layer
for param in model.base_model.encoder.layer[-1].parameters():
    param.requires_grad = True

# ----------------------------
# Tokenization
# ----------------------------
def tokenize_function(example):
    return tokenizer(example["text"], padding="max_length", truncation=True, max_length=64)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# ----------------------------
# Data Collator
# ----------------------------
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# ----------------------------
# Training Arguments
# ----------------------------
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=2,
    logging_dir="./logs",
)

# ----------------------------
# Compute Metrics (for accuracy + precision + recall + F1)
# ----------------------------
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary"
    )
    acc = accuracy_score(labels, preds)

    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# ----------------------------
# Trainer
# ----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics  # <--- ONLY CHANGE: prints accuracy
)

# ----------------------------
# Train
# ----------------------------
trainer.train()

# ----------------------------
# Evaluate
# ----------------------------
results = trainer.evaluate()
print( results)

# ----------------------------
# Save Baseline Model
# ----------------------------
trainer.model.save_pretrained("baseline_afroxlm_model")
tokenizer.save_pretrained("baseline_afroxlm_model")
print("Baseline AfroXLMR model saved ✅")