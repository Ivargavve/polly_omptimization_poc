from rouge_score import rouge_scorer

def rougeL(a, b):
    s = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    return s.score(a, b)['rougeL'].fmeasure
