# Updates knowledge tree with "patches"
import copy, json, jsonpatch, os
from datetime import datetime

# Find the JSON path to a category
def _find_cat_path(knowledge, name):
    if name in knowledge:
        return [name]
    for cat, cfg in knowledge.items():
        subs = cfg.get("sub_categories", {})
        if name in subs:
            return [cat, "sub_categories", name]
    return None

# Convert list of paths to JSON pointer format
def _json_path(parts):
    return "/" + "/".join(parts)

# Build a JSON patch to add new keywords to a category
def build_keyword_patch(knowledge, category, new_terms):
    path_base = _find_cat_path(knowledge, category)
    if not path_base:
        raise KeyError(f"Category not found: {category}")
    return [
        {"op": "add", "path": _json_path(path_base + ["keywords", "-"]), "value": kw}
        for kw in new_terms
    ]

# Build a JSON patch to update the instruction of a category
def build_instruction_patch(knowledge, category, new_instruction):
    path_base = _find_cat_path(knowledge, category)
    if not path_base:
        raise KeyError(f"Category not found: {category}")
    return [{"op": "replace", "path": _json_path(path_base + ["instruction"]), "value": new_instruction}]

# Apply a JSON patch to the knowledge tree (without modifying original)
def apply_patch(knowledge, patch):
    k_copy = copy.deepcopy(knowledge)
    return jsonpatch.apply_patch(k_copy, patch, in_place=False)

# Save patch and updated knowledge to timestamped JSON files
def save_outputs(patch, patched_knowledge, outdir="../outputs"):
    os.makedirs(os.path.join(outdir, "patches"), exist_ok=True)
    os.makedirs(os.path.join(outdir, "knowledge_versions"), exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pfile = os.path.join(outdir, "patches", f"patch_{ts}.json")
    kfile = os.path.join(outdir, "knowledge_versions", f"knowledge_{ts}.json")
    with open(pfile, "w", encoding="utf-8") as f:
        json.dump(patch, f, ensure_ascii=False, indent=2)
    with open(kfile, "w", encoding="utf-8") as f:
        json.dump(patched_knowledge, f, ensure_ascii=False, indent=2)
    return pfile, kfile
