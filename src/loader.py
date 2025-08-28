import json
import pandas as pd
from langdetect import detect, DetectorFactory

# Make language detection deterministic
DetectorFactory.seed = 0

# Only work with english data, for easier debugging
def is_lang(text, target="en"):
    try:
        return detect(text) == target
    except:
        return False

def load_runs(path="../data/polly_runs.json", lang="en", replies_must_be_english=True):
    with open(path, "r", encoding="utf-8") as f:
        df = pd.DataFrame(json.load(f))
    if lang:
        df = df[df["detected_language"] == lang]
    if replies_must_be_english:
        df = df[
            df["llm_reply"].apply(lambda x: is_lang(x, lang)) &
            df["human_reply"].apply(lambda x: is_lang(x, lang)) &
            df["incoming_email"].apply(lambda x: is_lang(x, lang))
        ]
    return df.reset_index(drop=True)

def load_knowledge(path="../data/polly_knowledge.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
