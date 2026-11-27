"""pure metric functions. no io, no state."""

from __future__ import annotations

from typing import Hashable, Iterable, Sequence


def recall_at_k(retrieved_ids: Sequence[Hashable], gold_ids: Iterable[Hashable], k: int) -> float:
    """fraction of gold ids that appear in the top k retrieved ids.

    an empty gold set gives 0.0 (unanswerable questions are scored separately).
    """
    if k <= 0:
        raise ValueError("k must be positive")
    gold = set(gold_ids)
    if not gold:
        return 0.0
    top_k = set(retrieved_ids[:k])
    return len(gold & top_k) / len(gold)


def reciprocal_rank(retrieved_ids: Sequence[Hashable], gold_ids: Iterable[Hashable]) -> float:
    """1 / rank of the first retrieved id that is gold, 0.0 if none is."""
    gold = set(gold_ids)
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in gold:
            return 1.0 / rank
    return 0.0


def mean(values: Iterable[float]) -> float | None:
    """arithmetic mean, or None for an empty list (no number beats a fake 0)."""
    values = list(values)
    if not values:
        return None
    return sum(values) / len(values)
