# questions

`gold.jsonl` holds the gold questions, one JSON object per line. it is empty until the week-1 questions are written.

## schema

```
{"id": "q001", "question": str, "answerable": bool, "gold_answer": str|null, "gold_passages": [{"doc_id": str, "start_char": int, "end_char": int, "text": str}], "tags": [str]}
```

- `id`: `q` followed by digits, unique across the file.
- `question`: the question as a user would ask it.
- `answerable`: false if the corpus does not contain the answer.
- `gold_answer`: short reference answer, or null when unanswerable.
- `gold_passages`: the passages that support the answer. `doc_id` matches a file in corpus/, `start_char`/`end_char` are offsets into that document's text (after the header), `text` is the exact slice.
- `tags`: free-form labels, e.g. `lookup`, `multi-passage`, `unanswerable`.

unanswerable questions have `answerable=false`, `gold_answer=null` and `gold_passages=[]`.

the formal version is `schema.json` (JSON Schema). `evals/gold.py` validates every line against the same rules with the stdlib only; run `python -m evals.run_eval` to check the file.
