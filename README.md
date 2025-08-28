# Polly Optimization POC

This repository is a proof of concept for Footways coding challenge.  
The goal with this project is to explore how Polly’s knowledge tree could be optimized.

## Contents

- Loads the runs log, and extracts the different data polly_runs.json. Loads the knowledge tree polly_knowledge.json.
- Filters to use only english as language for easier debugging.
- Computes the ROUGE-L value comparing the llm response and the human response.
- Goes through the runs log and prints out the 3 worst depicted cases.