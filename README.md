# Polly Optimization POC

This repository is a proof of concept for Footway’s coding challenge.  
The goal of this project is to explore how Polly’s knowledge tree could be optimized automatically, instead of relying only on manual human updates.

## What the project does

- Loads the **runs dataset** (`polly_runs.json`) containing logged customer interactions.
- Loads the **knowledge tree** (`polly_knowledge.json`) containing category definitions, keywords, and instructions.
- Filters runs to English only (for easier debugging).
- Evaluates baseline performance using:
  - **Keyword accuracy** (simple keyword-based classification).
  - **ROUGE-L** similarity score between Polly’s templated reply and the human reply.
- Suggests improvements:
  - **New keywords** based on frequent terms in the training data.
  - **Instruction hints** based on patterns in human replies.
- Builds and applies a **JSON patch** to update the knowledge tree automatically.
- Re-evaluates performance on a validation set (split by timestamp).
- Saves outputs:
  - JSON patch file
  - Updated knowledge tree
  - Markdown report summarizing metrics and improvements

Example report output can be found in `outputs/reports/last_run.md`.

---

## Setup instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd POLLY_OMPTIMIZATION_POC
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare data**  
   Place the following files inside the `data/` folder
   - `polly_knowledge.json`
   - `polly_runs.json`
---

## Running the pipeline

```bash
python main.py
```

---

## Outputs

After running

- **Patched knowledge tree** in `outputs/knowledge_versions/`
- **Patch JSON file** in `outputs/patches/`
- **Markdown report** in `outputs/reports/last_run.md`

The report includes
- Patch summary (keywords added, instructions changed)
- Baseline vs after-patch metrics
- Best improved example with before/after replies
- Paths to saved artifacts

---

## Example usage

By default, `main.py` looks for category `STATUS_SHIPPING` with cutoff date `2025-07-10`:

```bash
python main.py
```

This will:
Train on runs before July 15, 2025
Validate on runs after that date
Suggest keyword/instruction updates for the RETURN category
Save patch + report in outputs/

### Example output
Baseline (validation): {'keyword_accuracy': 0.075, 'rougeL_templ_vs_human': 0.14}
After patch (validation): {'keyword_accuracy': 0.178, 'rougeL_templ_vs_human': 0.122}
