from loader import load_runs, load_knowledge
from eval import rougeL

def main():
    runs = load_runs()
    ktree = load_knowledge()
    print(f"Loaded {len(runs)} runs, {len(ktree)} categories in knowledge tree")

    # show 3 worst cases according to score
    worst = runs.nsmallest(3, "score")[["incoming_email","llm_reply","human_reply","score","category"]]
    for _, row in worst.iterrows():
        r = rougeL(row["llm_reply"], row["human_reply"])
        print("\n--- Case ---")
        print("Category:", row["category"])
        print("Score (dataset):", round(row["score"],3), "ROUGE-L (our eval):", round(r,3))
        print(f"Incoming email: {row['incoming_email'][:200].replace('\n', ' ')}...")
        print("LLM reply:", row['llm_reply'][:200], "...")
        print("Human reply:", row['human_reply'][:200], "...")

if __name__ == "__main__":
    main()
