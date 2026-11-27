"""eval stub.

python -m evals.run_eval

loads questions/gold.jsonl (validated), writes runs/latest-stub.json with every
metric set to null, and exits 0. no retriever is wired yet, so nothing is
scored. stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.gold import GoldValidationError, load_gold

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GOLD = REPO_ROOT / "questions" / "gold.jsonl"
DEFAULT_OUT = REPO_ROOT / "runs" / "latest-stub.json"

METRIC_KEYS = (
    "recall_at_5",
    "mrr",
    "answer_correctness",
    "refusal_rate",
    "cost_usd",
    "latency_p50_s",
)


def run(gold_path: str | Path = DEFAULT_GOLD, out_path: str | Path = DEFAULT_OUT) -> dict:
    """load and validate the gold file, write the stub result, return it."""
    questions = load_gold(gold_path)
    n = len(questions)
    result: dict = {
        "status": "stub",
        "n_questions": n,
        "metrics": {key: None for key in METRIC_KEYS},
    }
    if n == 0:
        print("0 questions, nothing to score")
    else:
        note = f"{n} questions loaded and valid, but no retriever is wired yet; metrics left null"
        result["note"] = note
        print(note)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ragbench-agent eval stub")
    parser.add_argument("--gold", default=str(DEFAULT_GOLD), help="path to gold.jsonl")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="where to write the result json")
    args = parser.parse_args(argv)
    try:
        run(args.gold, args.out)
    except GoldValidationError as exc:
        print(f"invalid gold file: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
