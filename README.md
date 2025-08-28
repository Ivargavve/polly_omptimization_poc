# Polly Optimization POC

This repository is a proof of concept for Footway’s coding challenge.  
The goal of this project is to explore how Polly’s knowledge tree could be optimized automatically.

## What the project does

- Loads the runs log and extracts data from it.
- Loads the knowledge tree json.
- Filters runs to English only (easier debugging)
- Evaluate performance before patch using Keyword accuracy and Rouge-L value. Similarity score between Polly’s templated reply and the human reply.
- Suggests improvements with new keywords and instuction hints.
- Creates a patch that updates the knowledge tree automatically.
- Re-evaluates performance values comparing the original knowledge base and the new "patch"
- Output files are saved as a JSON patch file, an updated knowledge tree and a short report of what changes have been made and what values have changed with the new patch.

Example report output can be found in last_run.md.

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
   .venv\Scripts\activate
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

## usage

```bash
python main.py
```

### output
Before patch (validation): {'keyword_accuracy': 0.075, 'rougeL_templ_vs_human': 0.14}
After patch (validation): {'keyword_accuracy': 0.178, 'rougeL_templ_vs_human': 0.122}

Best improved example:

- ROUGE-L before: 0.049
- ROUGE-L after: 0.100
- correct_cat: STATUS_RETURN | pred before → after: HOW_TO_RETURN → STATUS_SHIPPING
...

This shows:
Keyword accuracy improved (better classification).
ROUGE-L changed slightly (different similarity between template and human reply).
The patch automatically updated the knowledge tree with new keywords/instructions.

###This proof of concept shows that
It's possible to automate the process of evaluating and optimizing the json file
from the emails using the human replies as reference. 
This makes knowledge tree maintenance scalable and reproducible even though this particular solution is only a poc and would not work great in practice :D
