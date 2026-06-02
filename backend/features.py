import string
import re

# ----------------------------
# Pidgin Keywords & Particles
# ----------------------------
pidgin_keywords = [
    "abeg", "wetin", "wahala", "dey", "sabi",
    "oga", "shey", "na", "go", "come",
    "no", "fit", "wan", "dem", "una",
    "make", "de", "don", "sef", "abi"
]

particles = ["na", "dey", "go", "don"]

# ----------------------------
# English Words
# ----------------------------
english_words = [
    "the", "is", "are", "you", "what", "how",
    "this", "that", "and", "to", "of", "in",
    "it", "for", "on", "with", "as", "was", "be"
]

# ----------------------------
# Slang
# ----------------------------
slang_words = ["abi", "sha", "nah", "lol", "lmao"]

# ----------------------------
# Normalize text
# ----------------------------
def normalize_text(text):
    return re.sub(r'(.)\\1{2,}', r'\\1', text)

# ----------------------------
# Helper Functions
# ----------------------------
def is_pidgin(word):
    return word in pidgin_keywords

def is_english(word):
    return word in english_words

# ----------------------------
# Feature Extraction
# ----------------------------
def extract_features(text):

    if not isinstance(text, str):
        return {
            "contains_pidgin": 0,
            "pidgin_count": 0,
            "particle_count": 0,
            "has_reduplication": 0,
            "switch_count": 0,
            "english_ratio": 0
        }

    # Normalize
    text = normalize_text(text)

    # Clean
    text_clean = text.lower().translate(str.maketrans('', '', string.punctuation))
    tokens = text_clean.split()
    total_words = len(tokens)

    # ----------------------------
    # Core Features (USED IN MODEL)
    # ----------------------------
    pidgin_count = sum(1 for word in tokens if word in pidgin_keywords)
    contains_pidgin = 1 if pidgin_count > 0 else 0
    particle_count = sum(1 for word in tokens if word in particles)

    has_reduplication = 1 if any(tokens[i] == tokens[i+1] for i in range(len(tokens)-1)) else 0

    english_count = sum(1 for word in tokens if word in english_words)
    english_ratio = english_count / total_words if total_words > 0 else 0

    switch_count = 0
    for i in range(len(tokens)-1):
        if (is_pidgin(tokens[i]) and is_english(tokens[i+1])) or \
           (is_english(tokens[i]) and is_pidgin(tokens[i+1])):
            switch_count += 1

    # ----------------------------
    # Return ONLY what model needs
    # ----------------------------
    return {
        "contains_pidgin": contains_pidgin,
        "pidgin_count": pidgin_count,
        "particle_count": particle_count,
        "has_reduplication": has_reduplication,
        "switch_count": switch_count,
        "english_ratio": english_ratio
    }