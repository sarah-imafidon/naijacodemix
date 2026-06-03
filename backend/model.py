import torch
import torch.nn as nn
import joblib
import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

# ----------------------------
# Google Drive File IDs
# ----------------------------
HYBRID_MODEL_ID      = "1ZpVvoAi2qCk-XayLwSmL1R-2CFb1lDUx"
SCALER_ID            = "1SrlSsQhaMv8IhepAfBDk9pBIMFhjRbqf"

# Baseline model files — individual IDs (more reliable than folder download)
BASELINE_FILES = {
    "config.json":            "11ComrT2PQ5q2DwpDe8HnTct4SwHlqgug",
    "model.safetensors":      "1sdJqFiIy9hV1EFVXEXk4XICo3ZP4Eq7D",
    "tokenizer.json":         "1s059qeEeyw6-v74ct3748U79wdp5iWkE",
    "tokenizer_config.json":  "1IKBgujRge4KkIsAQtLPzisUC8KSBDOtJ",
}

# ----------------------------
# Local paths (relative to project root)
# ----------------------------
BASE_DIR            = Path(__file__).parent.parent
HYBRID_MODEL_PATH   = BASE_DIR / "hybrid_afroxlm_model.pt"
SCALER_PATH         = BASE_DIR / "scaler.pkl"
BASELINE_MODEL_PATH = BASE_DIR / "baseline_afroxlm_model"


# ----------------------------
# Download helpers
# ----------------------------
def _download_file(file_id: str, dest: Path):
    """Download a single file from Google Drive using gdown."""
    import gdown
    print(f"Downloading {dest.name} from Google Drive...")
    gdown.download(
        id=file_id,
        output=str(dest),
        quiet=False,
        fuzzy=False
    )
    print(f"✅ {dest.name} downloaded.")


def _download_folder(baseline_files: dict, dest: Path):
    """Download baseline model files individually from Google Drive."""
    import gdown
    dest.mkdir(parents=True, exist_ok=True)
    print("Downloading baseline model files from Google Drive...")
    for filename, file_id in baseline_files.items():
        file_dest = dest / filename
        if not file_dest.exists():
            print(f"  Downloading {filename}...")
            gdown.download(
                id=file_id,
                output=str(file_dest),
                quiet=False,
                fuzzy=False
            )
            print(f"  ✅ {filename} downloaded.")
    print("✅ Baseline model folder complete.")


def _ensure_models():
    """
    Check if model files exist locally.
    If not, download them from Google Drive.
    """
    if not HYBRID_MODEL_PATH.exists():
        _download_file(HYBRID_MODEL_ID, HYBRID_MODEL_PATH)

    if not SCALER_PATH.exists():
        _download_file(SCALER_ID, SCALER_PATH)

    baseline_files_exist = all(
        (BASELINE_MODEL_PATH / fname).exists()
        for fname in BASELINE_FILES.keys()
    )
    if not baseline_files_exist:
        _download_folder(BASELINE_FILES, BASELINE_MODEL_PATH)


# ----------------------------
# Hybrid Model Definition
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
        outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        combined = torch.cat([cls_embedding, features], dim=1)
        x = self.fc1(combined)
        x = self.relu(x)
        logits = self.fc2(x)
        return logits


# ----------------------------
# Load Models Function
# ----------------------------
def load_models():

    # Download from Google Drive if files are missing
    _ensure_models()

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(BASELINE_MODEL_PATH))

    # Baseline model
    baseline_model = AutoModelForSequenceClassification.from_pretrained(
        str(BASELINE_MODEL_PATH)
    )
    baseline_model.eval()

    # Transformer backbone for hybrid
    transformer = AutoModel.from_pretrained(str(BASELINE_MODEL_PATH))

    # Hybrid model
    hybrid_model = HybridClassifier(transformer, feature_dim=6)
    hybrid_model.load_state_dict(
        torch.load(str(HYBRID_MODEL_PATH), map_location="cpu")
    )
    hybrid_model.eval()

    # Scaler
    scaler = joblib.load(str(SCALER_PATH))

    return tokenizer, baseline_model, hybrid_model, scaler