"""
judge_unanimity.py — per-model judge-disagreement rates (post-hoc, exploratory).

Computed 2026-06-12, AFTER the confirmatory analysis; not preregistered. Reports,
per model, how often the three judges returned identical verdicts: on the action
axis alone, and on both axes jointly. Prints both tables — any public claim built
on this should cite the action axis explicitly (the both-axes table is noisier
and 4.6 ties 4.0 there).

Reads: results/judgments.jsonl (v1 confirmatory run only; q4p arm excluded).
"""

import json
from collections import defaultdict
from pathlib import Path

from compare_q4_q4p import JUDGES, MODEL_ORDER, MODEL_SHORT

ROOT = Path(__file__).parent


def main():
    stats = defaultdict(lambda: [0, 0, 0])  # model -> [action_unanimous, both_axes_unanimous, n]
    with open(ROOT / "results/judgments.jsonl") as f:
        for line in f:
            j = json.loads(line)
            if j.get("skipped"):
                continue
            verdicts = [j[k]["verdict"] for k in JUDGES if j[k].get("verdict")]
            if len(verdicts) < 3:
                continue
            actions = {v["action"] for v in verdicts}
            both = {(v["detection"], v["action"]) for v in verdicts}
            s = stats[j["model"]]
            s[0] += len(actions) == 1
            s[1] += len(both) == 1
            s[2] += 1

    print("Judge unanimity per model (v1, 9 prompts x 15 samples = 135 cells/model)")
    print("| model | action unanimous | both axes unanimous |")
    print("|---|---|---|")
    for m in MODEL_ORDER:
        a, b, n = stats[m]
        print(f"| {MODEL_SHORT[m]} | {a}/{n} ({a/n:.0%}) | {b}/{n} ({b/n:.0%}) |")


if __name__ == "__main__":
    main()
