import torch
from backend.features import extract_features
from backend.model import load_models

# ----------------------------
# Load models ONCE
# ----------------------------
tokenizer, baseline_model, hybrid_model, scaler = load_models()


# ----------------------------
# Prediction Function
# ----------------------------
def predict(text):

    # ----------------------------
    # Extract Features
    # ----------------------------
    features = extract_features(text)

    # ----------------------------
    # Tokenize Text
    # ----------------------------
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=64
    )

    # ----------------------------
    # Baseline Prediction
    # ----------------------------
    with torch.no_grad():
        outputs = baseline_model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        conf = probs[0][pred].item()

    baseline_pred = "Code-Mixed" if pred == 1 else "Not Code-Mixed"

    # ----------------------------
    # Hybrid Prediction
    # ----------------------------
    feature_list = [[
        features["contains_pidgin"],
        features["pidgin_count"],
        features["particle_count"],
        features["has_reduplication"],
        features["switch_count"],
        features["english_ratio"]
    ]]

    # Scale features
    scaled_features = scaler.transform(feature_list)
    features_tensor = torch.tensor(scaled_features, dtype=torch.float32)

    with torch.no_grad():
        logits = hybrid_model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            features=features_tensor
        )
        probs = torch.softmax(logits, dim=1)
        pred_h = torch.argmax(probs, dim=1).item()
        conf_h = probs[0][pred_h].item()

    hybrid_pred = "Code-Mixed" if pred_h == 1 else "Not Code-Mixed"

    # ----------------------------
    # Return EVERYTHING cleanly
    # ----------------------------
    return {
        "baseline": {
            "prediction": baseline_pred,
            "confidence": round(conf, 2)
        },
        "hybrid": {
            "prediction": hybrid_pred,
            "confidence": round(conf_h, 2)
        },
        "features": features
    }