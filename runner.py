"""
runner.py — calls each Claude Opus model with each prompt, N samples per cell.

Writes results/responses.jsonl: one line per (model, prompt_id, sample_idx).
Each line records thinking (if available), response text, token usage, and
whether adaptive thinking auto-triggered (relevant for 4.7).
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

import yaml
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / "responses.jsonl"

# Per-model thinking config.
#   None          -> no thinking parameter, model is pre-reasoning era
#   "adaptive"    -> no thinking parameter, model may auto-trigger thinking
#   dict          -> passed to API as-is
# max_tokens differs by model — Claude 3 Opus enforces a 4096 server-side cap,
# whereas 4.x models accept 16000 (needed for thinking budget + response).
MODEL_CONFIG = {
    "claude-3-opus-20240229":   {"thinking": None,                                          "max_tokens":  4096},
    "claude-opus-4-20250514":   {"thinking": {"type": "enabled", "budget_tokens": 10000},   "max_tokens": 16000},
    "claude-opus-4-1-20250805": {"thinking": {"type": "enabled", "budget_tokens": 10000},   "max_tokens": 16000},
    "claude-opus-4-5-20251101": {"thinking": {"type": "enabled", "budget_tokens": 10000},   "max_tokens": 16000},
    "claude-opus-4-6":          {"thinking": {"type": "enabled", "budget_tokens": 10000},   "max_tokens": 16000},
    "claude-opus-4-7":          {"thinking": "adaptive",                                    "max_tokens": 16000},
}

SAMPLES_PER_CELL = 15
TEMPERATURE = 1.0          # required by thinking mode; matched across all models
CONCURRENCY = 8            # tune down if rate limits bite

client = AsyncAnthropic()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Claude Opus models against intent-detection prompts."
    )
    parser.add_argument(
        "--smoke", action="store_true",
        help="quick test: 3 models (one per thinking-config path), q1 only, 1 sample",
    )
    parser.add_argument(
        "--models", nargs="+", metavar="MODEL",
        help="subset of models to run (default: all in MODEL_CONFIG)",
    )
    parser.add_argument(
        "--prompts", nargs="+", metavar="ID",
        help="subset of prompt ids, e.g. q1 q2 (default: all in prompts.yaml)",
    )
    parser.add_argument(
        "--samples", type=int, metavar="N",
        help=f"override samples per cell (default: {SAMPLES_PER_CELL})",
    )
    parser.add_argument(
        "--output", metavar="PATH",
        help="output file path (default: results/responses.jsonl)",
    )
    return parser.parse_args()


async def call_one(
    model: str,
    prompt_id: str,
    prompt_text: str,
    sample_idx: int,
    semaphore: asyncio.Semaphore,
) -> dict:
    """One API call. Returns a dict suitable for JSONL serialization."""
    async with semaphore:
        config = MODEL_CONFIG[model]
        kwargs = {
            "model": model,
            "max_tokens": config["max_tokens"],
            "temperature": TEMPERATURE,
            "messages": [{"role": "user", "content": prompt_text}],
        }

        thinking_cfg = config["thinking"]
        if isinstance(thinking_cfg, dict):
            kwargs["thinking"] = thinking_cfg
        # "adaptive" or None: omit thinking parameter entirely

        start = time.time()
        try:
            # Streaming required by Anthropic for long/thinking-enabled requests;
            # using it uniformly for all calls keeps the path simple.
            async with client.messages.stream(**kwargs) as stream:
                resp = await stream.get_final_message()
            elapsed = time.time() - start

            thinking_text = ""
            response_text = ""
            for block in resp.content:
                btype = getattr(block, "type", None)
                if btype == "thinking":
                    thinking_text = getattr(block, "thinking", "") or ""
                elif btype == "text":
                    response_text = getattr(block, "text", "") or ""

            return {
                "model": model,
                "prompt_id": prompt_id,
                "sample_idx": sample_idx,
                "thinking_available": bool(thinking_text),
                "thinking": thinking_text,
                "response": response_text,
                "stop_reason": resp.stop_reason,
                "usage": {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                },
                "elapsed_s": round(elapsed, 2),
                "error": None,
            }
        except Exception as e:
            return {
                "model": model,
                "prompt_id": prompt_id,
                "sample_idx": sample_idx,
                "thinking_available": False,
                "thinking": "",
                "response": "",
                "stop_reason": None,
                "usage": None,
                "elapsed_s": round(time.time() - start, 2),
                "error": f"{type(e).__name__}: {e}",
            }


async def main():
    args = parse_args()

    with open(ROOT / "prompts.yaml") as f:
        all_prompts = yaml.safe_load(f)["prompts"]

    # Resolve run scope from args.
    if args.smoke:
        models = ["claude-3-opus-20240229", "claude-opus-4-1-20250805", "claude-opus-4-7"]
        prompt_ids = ["q1"]
        samples = 1
    else:
        models = args.models or list(MODEL_CONFIG.keys())
        prompt_ids = args.prompts or [p["id"] for p in all_prompts]
        samples = args.samples if args.samples is not None else SAMPLES_PER_CELL

    # Validate.
    unknown_models = [m for m in models if m not in MODEL_CONFIG]
    if unknown_models:
        raise ValueError(
            f"Unknown models: {unknown_models}. Known: {list(MODEL_CONFIG.keys())}"
        )
    prompts = [p for p in all_prompts if p["id"] in prompt_ids]
    missing = set(prompt_ids) - {p["id"] for p in prompts}
    if missing:
        raise ValueError(f"Unknown prompt ids: {missing}")

    output_path = Path(args.output) if args.output else OUTPUT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(CONCURRENCY)
    tasks = []
    for model in models:
        for p in prompts:
            for i in range(samples):
                tasks.append(call_one(model, p["id"], p["text"], i, semaphore))

    print(f"Dispatching {len(tasks)} calls (concurrency={CONCURRENCY})")
    print(f"  models:  {models}")
    print(f"  prompts: {prompt_ids}")
    print(f"  samples: {samples}")
    print(f"  output:  {output_path}")
    print()

    with open(output_path, "w") as f:
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            f.write(json.dumps(result) + "\n")
            f.flush()
            completed += 1
            status = "ERR" if result.get("error") else "OK "
            thinking_flag = "T" if result.get("thinking_available") else "-"
            print(
                f"[{completed:3d}/{len(tasks)}] {status} {thinking_flag} "
                f"{result['model']:30s} {result['prompt_id']}#{result['sample_idx']} "
                f"({result.get('elapsed_s', 0):.1f}s)"
                + (f"  {result['error']}" if result.get("error") else "")
            )

    print(f"\nDone. {completed} results at {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
