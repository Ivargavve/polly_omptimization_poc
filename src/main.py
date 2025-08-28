import argparse
import os
from datetime import datetime

from loader import load_runs, load_knowledge
from eval import rougeL
from router import route_email, compose_reply
from miner import suggest_keywords, suggest_instruction_hint
from patcher import build_keyword_patch, build_instruction_patch, apply_patch, save_outputs

# Get category configuration
def get_cat_cfg(tree, name):
    if name in tree:
        return tree[name]
    for _, cfg in tree.items():
        subs = cfg.get("sub_categories", {})
        if name in subs:
            return subs[name]
    return {}

# Evaluate model predictions vs human replies
def evaluate(df, knowledge):
    hits, rouge_sum, out = 0, 0.0, []
    for _, r in df.iterrows():
        pred = route_email(r["incoming_email"], knowledge)
        hits += 1 if pred == r["category"] else 0
        cfg = get_cat_cfg(knowledge, pred) or get_cat_cfg(knowledge, r["category"])
        templ = compose_reply(r["incoming_email"], cfg or {})
        rL = rougeL(templ, r["human_reply"])
        rouge_sum += rL
        out.append({
            "pred": pred, "correct_cat": r["category"], "rouge": rL,
            "incoming": r["incoming_email"], "templated": templ, "human": r["human_reply"],
            "dataset_score": r.get("score", None)
        })
    n = max(len(df), 1)
    return {"keyword_accuracy": hits/n, "rougeL_templ_vs_human": rouge_sum/n}, out

# Split dataset into train and validation by timestamp
def split_by_time(df, val_cutoff_iso):
    train = df[df["final_ts"] < val_cutoff_iso]
    val = df[df["final_ts"] >= val_cutoff_iso]
    return train, val

# Summarize patch operations (keywords added, instruction changed)
def parse_patch_summary(patch_ops):
    added_keywords = []
    instruction_changed = False
    for op in patch_ops:
        if op.get("op") == "add" and "/keywords/" in op.get("path", ""):
            added_keywords.append(str(op.get("value")))
        if op.get("op") == "replace" and op.get("path", "").endswith("/instruction"):
            instruction_changed = True
    return added_keywords, instruction_changed

def main():
    # CLI args with default values, example category etc.
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="STATUS_SHIPPING")
    ap.add_argument("--val_cutoff", default="2025-07-10")
    ap.add_argument("--max_keywords", type=int, default=3)
    args = ap.parse_args()

    # load data
    runs = load_runs(lang="en", replies_must_be_english=True)
    ktree = load_knowledge()
    print(f"Loaded {len(runs)} runs, {len(ktree)} categories in knowledge tree")

    # show single worst case from dataset Rouge-L score
    worst = runs.nsmallest(1, "score")[["incoming_email","llm_reply","human_reply","score","category"]]
    for _, row in worst.iterrows():
        r = rougeL(row["llm_reply"], row["human_reply"])
        print("\n--- Example Worst English Case according to Rouge-L value ---")
        print("Category:", row["category"])
        print("Rouge-L (dataset):", round(row["score"],3), ", ROUGE-L (poc_eval):", round(r,3))
        print(f"Incoming email: {row['incoming_email'][:100].replace('\n', ' ')}...")
        print("LLM reply:", row['llm_reply'][:100], "...")
        print("Human reply:", row['human_reply'][:100], "...")

    train_df, val_df = split_by_time(runs, args.val_cutoff)
    if len(train_df) == 0 or len(val_df) == 0:
        print("\nWarning: empty train/val split. Adjust --val_cutoff.")
        return

    # Before patch evaluation
    base_metrics, base_rows = evaluate(val_df, ktree)
    print("\nBefore patch (validation):", {k: round(v,3) for k,v in base_metrics.items()})

    # Generate patch (keywords + instruction hints)
    patch_ops = []
    cands = suggest_keywords(train_df, ktree, args.category, max_new=args.max_keywords)
    if cands:
        patch_ops += build_keyword_patch(ktree, args.category, cands)

    hint = suggest_instruction_hint(train_df, args.category)
    if hint:
        current_instr = get_cat_cfg(ktree, args.category).get("instruction", "")
        new_instr = current_instr if hint in current_instr else (current_instr + "\n- " + hint).strip()
        patch_ops += build_instruction_patch(ktree, args.category, new_instr)

    if not patch_ops:
        print("\nNo patch candidates found. Try another category or tweak miners.")
        return

    # Apply patches to knowledge tree and re-evaluate
    ktree_patched = apply_patch(ktree, patch_ops)
    after_metrics, after_rows = evaluate(val_df, ktree_patched)

    # find best improved example after patch for the report
    improvements = []
    for b, a in zip(base_rows, after_rows):
        delta = a["rouge"] - b["rouge"]
        improvements.append({
            "delta": delta,
            "rouge_before": b["rouge"],
            "rouge_after": a["rouge"],
            "pred_before": b["pred"],
            "pred_after": a["pred"],
            "correct_cat": b["correct_cat"],
            "incoming": b["incoming"],
            "templated_before": b["templated"],
            "templated_after": a["templated"],
            "human": b["human"]
        })
    best = max(improvements, key=lambda x: x["delta"])
    print("After patch (validation):", {k: round(v,3) for k,v in after_metrics.items()})

    patch_file, knowledge_file = save_outputs(patch_ops, ktree_patched, outdir="../outputs")

    # write a short report of changes from the latest patch and best improved example
    report_path = "../outputs/reports/last_run.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    added_keywords, instr_changed = parse_patch_summary(patch_ops)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# POC Report\n\n")
        f.write(f"Date: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Category: {args.category}\n")
        f.write(f"Validation cutoff: {args.val_cutoff}\n\n")

        f.write("Patch summary:\n")
        f.write(f"- added keywords: {added_keywords if added_keywords else '[]'}\n")
        f.write(f"- instruction changed: {instr_changed}\n\n")

        f.write("Before patch metrics:\n")
        f.write(f"- keyword_accuracy: {base_metrics['keyword_accuracy']:.3f}\n")
        f.write(f"- rougeL_templ_vs_human: {base_metrics['rougeL_templ_vs_human']:.3f}\n\n")

        f.write("After patch metrics:\n")
        f.write(f"- keyword_accuracy: {after_metrics['keyword_accuracy']:.3f}\n")
        f.write(f"- rougeL_templ_vs_human: {after_metrics['rougeL_templ_vs_human']:.3f}\n\n")
        
        f.write("Best improved example:\n\n")
        f.write(f"- ROUGE-L before: {best['rouge_before']:.3f}\n")
        f.write(f"- ROUGE-L after: {best['rouge_after']:.3f}\n")
        f.write(f"- correct_cat: {best['correct_cat']} | pred before → after: {best['pred_before']} → {best['pred_after']}\n")
        f.write(f"- incoming: {best['incoming'][:200].replace(chr(10),' ')}...\n")
        f.write(f"- templated BEFORE: {best['templated_before'][:200]}...\n")
        f.write(f"- templated AFTER: {best['templated_after'][:200]}...\n")
        f.write(f"- human: {best['human'][:200]}...\n\n")

        f.write(f"Patch file: {patch_file}\n")
        f.write(f"Patched knowledge: {knowledge_file}\n")

    print("\nArtifacts saved:")
    print("patch:", patch_file)
    print("patched knowledge:", knowledge_file)
    print("report:", report_path)

if __name__ == "__main__":
    main()
