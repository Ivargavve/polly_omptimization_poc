import json
import pandas as pd

def load_runs(path="../data/polly_runs.json"):
    with open(path, "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

def load_knowledge(path="../data/polly_knowledge.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
