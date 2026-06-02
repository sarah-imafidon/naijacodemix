import torch
import torch.nn as nn
import joblib
import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

# ----------------------------
# Google Drive File IDs
# ----------------------------
HYBRID_MODEL_ID      = "1RD_5upvNjTCtRauVOVC-yxwmN2x8QCOD"
SCALER_ID            = "18yc8citNOhIhrZoPerzKsAWURWV2cSJF"
BASELINE_FOLDER_ID   = "1xIn3a6AOYM8JuGXX0Jza98hb1UzhwyrY"

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
    # Use uc?export=download&confirm=t to bypass large file warning
    url = f"https://drive.google.com/uc?export=download&confirm=t&id={file_id}"
    gdown.download(
        url=url,
        output=str(dest),
        quiet=False,
        resume=True
    )
    print(f"✅ {dest.name} downloaded.")


def _download_folder(folder_id: str, dest: Path):
    """Download an entire folder from Google Drive using gdown."""
    import gdown
    print(f"Downloading baseline model folder from Google Drive...")
    gdown.download_folder(
        f"https://drive.google.com/drive/folders/{folder_id}",
        output=str(dest),
        quiet=False,
        use_cookies=False
    )
    print(f"✅ Baseline model folder downloaded.")


def _ensure_models():
    """
    Check if model files exist locally.
    If not, download them from Google Drive.
    Only runs downloads on Streamlit Cloud (or any machine missing the files).
    """
    if not HYBRID_MODEL_PATH.exists():
        _download_file(HYBRID_MODEL_ID, HYBRID_MODEL_PATH)

    if not SCALER_PATH.exists():
        _download_file(SCALER_ID, SCALER_PATH)

    if not BASELINE_MODEL_PATH.exists() or not any(BASELINE_MODEL_PATH.iterdir()):
        BASELINE_MODEL_PATH.mkdir(parents=True, exist_ok=True)
        _download_folder(BASELINE_FOLDER_ID, BASELINE_MODEL_PATH)


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