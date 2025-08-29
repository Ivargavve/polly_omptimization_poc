# Polly proxy, suggest improvements such as keywords and hints.
from collections import Counter
import re

# Find category configuration (check both top-level and subcategories)
def _get_cat_cfg(knowledge, name):
    if name in knowledge:
        return knowledge[name]
    for _, cfg in knowledge.items():
        subs = cfg.get("sub_categories", {})
        if name in subs:
            return subs[name]
    return {}

# Suggest new keywords for a category by analyzing emails
def suggest_keywords(train_df, knowledge, category, max_new=3):
    # Take all training emails for the given category.
    # Extract frequent words with 4 or more letters.
    # Remove ones already in the knowledge tree.
    # Return new keyword suggestions.

    subset = train_df[train_df["category"] == category]
    text = " ".join(subset["incoming_email"].tolist()).lower()
    tokens = re.findall(r"[a-z]{4,}", text)

    freq = Counter(tokens)
    existing = {kw.lower() for kw in _get_cat_cfg(knowledge, category).get("keywords", [])}
    candidates = [w for w, _ in freq.most_common(50) if w not in existing]

    return candidates[:max_new]

# Suggest hints for writing better instructions
def suggest_instruction_hint(train_df, category):
    # If human replies mention 'tracking', suggest adding a tracking reminder.
    # If 'refund' is mentioned, suggest adding refund time info.

    subset = train_df[train_df["category"] == category]
    text = " ".join(subset["human_reply"].tolist()).lower()
    if "tracking" in text:
        return "Add reminder to include tracking information if available."
    if "refund" in text:
        return "Emphasize refund timeframe in reply."
    return None
