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
    dest.parent.mkdir(parents=True, exist_ok=True)
    gdown.download(
        id=file_id,
        output=str(dest),
        quiet=False,
        fuzzy=True
    )
    print(f"✅ {dest.name} downloaded.")


def _download_folder(baseline_files: dict, dest: Path):
    """Download baseline model files individually from Google Drive."""
    dest.mkdir(parents=True, exist_ok=True)
    print("Downloading baseline model files from Google Drive...")
    for filename, file_id in baseline_files.items():
        file_dest = dest / filename
        if not file_dest.exists():
            print(f"  Downloading {filename}...")
            _download_file(file_id, file_dest)
    print("✅ Baseline model folder complete.")


def _is_valid_file(path: Path, min_size_mb: float = 1.0) -> bool:
    """Check if a file exists and is larger than the minimum size."""
    return path.exists() and path.stat().st_size > min_size_mb * 1024 * 1024


def _ensure_models():
    """
    Check if model files exist and are valid.
    If not, download them from Google Drive.
    """
    # Hybrid model — check size > 100MB
    if not _is_valid_file(HYBRID_MODEL_PATH, min_size_mb=100):
        if HYBRID_MODEL_PATH.exists():
            print(f"⚠️ {HYBRID_MODEL_PATH.name} appears corrupted. Re-downloading...")
            HYBRID_MODEL_PATH.unlink()
        _download_file(HYBRID_MODEL_ID, HYBRID_MODEL_PATH)

    # Scaler — check size > 1KB
    if not _is_valid_file(SCALER_PATH, min_size_mb=0.001):
        if SCALER_PATH.exists():
            SCALER_PATH.unlink()
        _download_file(SCALER_ID, SCALER_PATH)

    # Baseline model files — check each one
    for filename, file_id in BASELINE_FILES.items():
        file_path = BASELINE_MODEL_PATH / filename
        min_size = 100 if filename == "model.safetensors" else 0.001
        if not _is_valid_file(file_path, min_size_mb=min_size):
            if file_path.exists():
                print(f"⚠️ {filename} appears corrupted. Re-downloading...")
                file_path.unlink()
            print(f"  Downloading {filename}...")
            _download_file(file_id, file_path)


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