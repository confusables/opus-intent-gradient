"""
make_pilot_packet.py — emit the model-BLIND assumption-profile pilot packet.

Reads thinking traces from the results files and writes a paste-ready packet
(reports/assumption_profile_pilot_packet.md) containing trace text ONLY — no
model names, no prompt ids — under neutral labels P1..Pn in a fixed shuffled
order. The un-blinding key lives in the rubric (§10), NOT here.

Usage: .venv/bin/python make_pilot_packet.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"

# (label, results-file, model, prompt_id, sample_idx) — order is the shuffle the
# raters see. Keep models/conditions interleaved so the sequence leaks nothing.
PILOT = [
    ("P1", "responses_4_0_bank_v2.jsonl", "claude-opus-4-20250514",   "q1",  12),
    ("P2", "responses.jsonl",             "claude-opus-4-5-20251101", "q7",  0),
    ("P3", "responses_4_0_bank_v2.jsonl", "claude-opus-4-20250514",   "q1c", 0),
    ("P4", "responses.jsonl",             "claude-opus-4-6",          "q7",  0),
    ("P5", "responses_4_0_bank_v2.jsonl", "claude-opus-4-20250514",   "q7",  0),
    ("P6", "responses.jsonl",             "claude-opus-4-5-20251101", "q8",  0),
    ("P7", "responses_4_0_bank_v2.jsonl", "claude-opus-4-20250514",   "q7c", 0),
    ("P8", "responses_4_0_bank_v2.jsonl", "claude-opus-4-20250514",   "q8",  0),
]

INSTRUCTION = (
    "You are coding short excerpts of an AI assistant's private reasoning. For "
    "each excerpt, score dimensions D1-D4 from the rubric (1, 2, 3, or N/A) and "
    "add one short phrase of justification per score. Do not guess which AI "
    "produced it. There are no right answers we are checking you against - we are "
    "checking whether the rubric is clear."
)


def _cache(fname):
    rows = {}
    for line in open(RESULTS / fname):
        r = json.loads(line)
        rows[(r["model"], r["prompt_id"], r["sample_idx"])] = r
    return rows


def main():
    caches = {}
    out = ["# Assumption-Profile Pilot Packet (BLIND)\n",
           "Pair with rubric §3-§6. Do NOT consult the rubric's §10 key while coding.\n",
           f"**Instruction:** {INSTRUCTION}\n", "---\n"]
    for label, fname, model, pid, idx in PILOT:
        caches.setdefault(fname, None)
        if caches[fname] is None:
            caches[fname] = _cache(fname)
        r = caches[fname].get((model, pid, idx))
        if r is None:
            raise SystemExit(f"missing cell: {model} {pid}#{idx} in {fname}")
        thinking = (r.get("thinking") or "").strip()
        if not thinking:
            raise SystemExit(f"empty trace: {label} ({model} {pid}#{idx})")
        out.append(f"### {label}\n\n{thinking}\n")

    dest = ROOT / "reports" / "assumption_profile_pilot_packet.md"
    dest.write_text("\n".join(out) + "\n")
    print(f"wrote {len([1 for _ in PILOT])} blind traces -> {dest}")


if __name__ == "__main__":
    main()
