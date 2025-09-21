import re

# ----------------------------
# Logical Fallacies (Expanded)
# ----------------------------
FALLACY_PATTERNS = {
    "Ad Hominem": [
        r"\bidiot\b", r"\bfool\b", r"\bstupid\b", r"\bcorrupt\b", r"\bdumb\b"
    ],
    "Strawman": [
        r"\bso you mean\b", r"\bwhat you(?:'| a)re saying\b"
    ],
    "False Cause": [
        r"\bbecause of this\b", r"\btherefore it caused\b",
        r"\bled to\b", r"\bresulted in\b"
    ],
    "Appeal to Authority": [
        r"\bexperts (agree|say|claim)\b", r"\bscientists (say|claim)\b",
        r"\bas everyone knows\b"
    ],
    "Slippery Slope": [
        r"\bif this happens.*(collapse|disaster|ruin|end)\b"
    ],
    "Bandwagon": [
        r"\beveryone (knows|believes|does)\b", r"\bmajority (say|think)\b"
    ],
    "False Dichotomy": [
        r"\beither.*or\b", r"\bno other choice\b", r"\bonly two options\b"
    ],
    "Hasty Generalization": [
        r"\ball\b.*\b(are|is)\b", r"\bnever\b", r"\balways\b"
    ],
    "Red Herring": [
        r"\bthat.s not the point\b", r"\bignore that\b", r"\bwhat about\b"
    ],
    "Circular Reasoning": [
        r"\bbecause I said so\b", r"\bit.s true because\b"
    ],
    "Appeal to Emotion": [
        r"\bthink of the children\b", r"\bhorrific\b", r"\btragic\b",
        r"\bheartbreaking\b"
    ],
    "Loaded Language": [
        r"\bdisaster\b", r"\bcatastrophe\b", r"\btraitor\b", r"\bhero\b"
    ],
    "False Analogy": [
        r"\bjust like\b", r"\bsimilar to\b"
    ],
    "Appeal to Tradition": [
        r"\bas it has always been\b", r"\bwe.ve always done it this way\b"
    ],
    "Appeal to Ignorance": [
        r"\bno one has proven\b", r"\bnot been disproven\b"
    ]
}

# ----------------------------
# Bias Categories
# ----------------------------
BIAS_PATTERNS = {
    "Emotional Bias": [
        r"\bterrible\b", r"\bhorrible\b", r"\bmiracle\b", r"\bevildoer\b"
    ],
    "Framing Bias": [
        r"\balways\b", r"\bnever\b", r"\beveryone knows\b", r"\bclearly\b"
    ],
    "Selection Bias": [
        r"\bonly mentions\b", r"\bignores\b", r"\bfails to include\b"
    ],
    "Confirmation Bias": [
        r"\bconfirms what I already knew\b", r"\bproves my point\b"
    ],
    "Ideological Bias": [
        r"\bliberal\b", r"\bconservative\b", r"\bsocialist\b", r"\bnationalist\b"
    ],
    "Religious Bias": [
        r"\bdivine\b", r"\bholy\b", r"\bsacred\b", r"\bblasphemy\b"
    ],
    "Cultural Bias": [
        r"\bwestern\b", r"\beastern\b", r"\btraditional\b"
    ],
    "Political Bias": [
        r"\bleft-wing\b", r"\bright-wing\b", r"\bpartisan\b"
    ]
}

# ----------------------------
# Detection Function
# ----------------------------
def detect_patterns(text: str) -> dict:
    """
    Detect fallacies and biases in text using regex patterns.
    Returns structured dict: {"fallacies": [...], "biases": [...]}
    """
    fallacies = []
    biases = []

    for fallacy, patterns in FALLACY_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                fallacies.append(fallacy)
                break  # avoid duplicates

    for bias, patterns in BIAS_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                biases.append(bias)
                break  # avoid duplicates

    # Deduplicate and sort for consistency
    fallacies = sorted(list(set(fallacies)))
    biases = sorted(list(set(biases)))

    return {"fallacies": fallacies, "biases": biases}
