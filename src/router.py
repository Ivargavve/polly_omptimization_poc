# Polly proxy, classification
import re

# Iterate over all categories and their subcategories
def _iter_categories(tree):
    for cat, cfg in tree.items():
        yield cat, cfg
        for sub, scfg in cfg.get("sub_categories", {}).items():
            yield sub, scfg

# Classify an email text based on keyword matches
def route_email(email_text, knowledge):
    scores = {}
    for cat, cfg in _iter_categories(knowledge):
        count = sum(1 for kw in cfg.get("keywords", [])
                    if re.search(r"\b" + re.escape(kw) + r"\b", email_text, re.I))
        scores[cat] = count

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "UNCLEAR"

# Generate a reply message based on the chosen category
def compose_reply(email_text, cat_cfg):
    instr = cat_cfg.get("instruction", "We will handle your request soon.")
    return f"Hello! Thanks for your message. {instr}"
