"""load and validate questions/gold.jsonl (stdlib only).

mirrors questions/schema.json by hand so evals stay dependency-free.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_ID_RE = re.compile(r"^q[0-9]+$")
_TOP_KEYS = {"id", "question", "answerable", "gold_answer", "gold_passages", "tags"}
_PASSAGE_KEYS = {"doc_id", "start_char", "end_char", "text"}


class GoldValidationError(ValueError):
    pass


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_question(obj: Any) -> list[str]:
    """return a list of problems with one gold question; empty means valid."""
    if not isinstance(obj, dict):
        return ["not a JSON object"]
    errors: list[str] = []
    missing = _TOP_KEYS - obj.keys()
    extra = obj.keys() - _TOP_KEYS
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected keys: {sorted(extra)}")

    qid = obj.get("id")
    if "id" in obj and not (isinstance(qid, str) and _ID_RE.match(qid)):
        errors.append("id must be a string like 'q001'")
    if "question" in obj and not (isinstance(obj["question"], str) and obj["question"]):
        errors.append("question must be a non-empty string")
    answerable = obj.get("answerable")
    if "answerable" in obj and not isinstance(answerable, bool):
        errors.append("answerable must be a bool")
    answer = obj.get("gold_answer")
    if "gold_answer" in obj and not (answer is None or isinstance(answer, str)):
        errors.append("gold_answer must be a string or null")

    passages = obj.get("gold_passages")
    if "gold_passages" in obj:
        if not isinstance(passages, list):
            errors.append("gold_passages must be a list")
            passages = None
        else:
            for i, p in enumerate(passages):
                errors.extend(f"gold_passages[{i}]: {e}" for e in _validate_passage(p))

    tags = obj.get("tags")
    if "tags" in obj and not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
        errors.append("tags must be a list of strings")

    if answerable is False:
        if answer is not None:
            errors.append("unanswerable question must have gold_answer=null")
        if passages:
            errors.append("unanswerable question must have gold_passages=[]")
    elif answerable is True:
        if not (isinstance(answer, str) and answer):
            errors.append("answerable question needs a non-empty gold_answer")
        if isinstance(passages, list) and not passages:
            errors.append("answerable question needs at least one gold passage")
    return errors


def _validate_passage(p: Any) -> list[str]:
    if not isinstance(p, dict):
        return ["not a JSON object"]
    errors: list[str] = []
    missing = _PASSAGE_KEYS - p.keys()
    extra = p.keys() - _PASSAGE_KEYS
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected keys: {sorted(extra)}")
    if "doc_id" in p and not (isinstance(p["doc_id"], str) and p["doc_id"]):
        errors.append("doc_id must be a non-empty string")
    for key in ("start_char", "end_char"):
        if key in p and not (_is_int(p[key]) and p[key] >= 0):
            errors.append(f"{key} must be a non-negative integer")
    if _is_int(p.get("start_char")) and _is_int(p.get("end_char")) and p["end_char"] < p["start_char"]:
        errors.append("end_char must be >= start_char")
    if "text" in p and not isinstance(p["text"], str):
        errors.append("text must be a string")
    return errors


def load_gold(path: str | Path) -> list[dict[str, Any]]:
    """read a gold.jsonl file, validate every line, raise on any problem.

    blank lines are skipped. ids must be unique.
    """
    path = Path(path)
    questions: list[dict[str, Any]] = []
    problems: list[str] = []
    seen: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                problems.append(f"line {lineno}: invalid JSON ({exc.msg})")
                continue
            errs = validate_question(obj)
            problems.extend(f"line {lineno}: {e}" for e in errs)
            if not errs:
                if obj["id"] in seen:
                    problems.append(f"line {lineno}: duplicate id {obj['id']}")
                seen.add(obj["id"])
                questions.append(obj)
    if problems:
        raise GoldValidationError(f"{path}: " + "; ".join(problems))
    return questions
