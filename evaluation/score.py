from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def exact_match(pred: str, ref: str) -> float:
    return float(pred.strip().lower() == ref.strip().lower())

def token_f1(pred: str, ref: str) -> float:
    p = pred.lower().split(); r = ref.lower().split()
    if not p or not r: return float(p == r)
    from collections import Counter
    common = sum((Counter(p) & Counter(r)).values())
    if common == 0: return 0.0
    precision = common / len(p); recall = common / len(r)
    return 2 * precision * recall / (precision + recall)

def normalized_mean(values: list[float]) -> float:
    return 100.0 * (sum(values) / len(values)) if values else 0.0

def score_file(path: str) -> dict:
    rows = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    em=[]; f1=[]
    for row in rows:
        pred=str(row.get("prediction", "")); ref=str(row.get("reference", ""))
        em.append(exact_match(pred, ref)); f1.append(token_f1(pred, ref))
    return {"samples":len(rows), "exact_match":normalized_mean(em), "token_f1":normalized_mean(f1)}

if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("predictions"); args=ap.parse_args()
    print(json.dumps(score_file(args.predictions), indent=2))
