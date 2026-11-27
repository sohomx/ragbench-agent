# ragbench-agent

a research agent over a real, messy corpus, with its own retrieval benchmark, eval suite and recorded-trace harness. numbers first.

## results

| run | date | corpus | questions | recall@k (k=5) | mrr | answer correctness | refusal rate | cost / question (usd) | p50 latency (s) |
|-----|------|--------|-----------|----------------|-----|--------------------|--------------|-----------------------|-----------------|
| -   | -    | -      | -         | -              | -   | -                  | -            | -                     | -               |

status: no runs yet, baseline due in week 2.

every number in this table links to a result file in runs/. no file, no claim.

## status

week 1 of 12. see [WEEK1.md](WEEK1.md).

## the 12-week plan

- week 1 (30 nov): pick corpus, scrape and clean it, write 30 gold questions with gold passages, repo skeleton + CI, readme stub
- week 2: baseline RAG (fixed chunks, dense retrieval, plain answer), run the 30 questions, log recall@k, publish first number even if bad
- week 3: grow to 100 questions incl. 20 unanswerable, scoring script, results committed as json
- week 4: retrieval ablations (chunk size, overlap, hybrid bm25+dense, reranker): one table, one winner
- week 5: agent harness v1: tool loop, state object, step/token budgets, timeouts, every run writes a trace file
- week 6: replay tool: rerun any trace deterministically with a stubbed model
- week 7: error analysis: read 100 traces by hand, written failure taxonomy with counts
- week 8: LLM judge for answer correctness and citation support, calibrated against 100 hand labels, report agreement
- week 9: CI gate: fixed subset on every PR, fail on recall/judged accuracy drop past threshold; cost and latency per run
- week 10: harden: prompt injection in documents, tool failure injection, refusal behavior, 20 adversarial cases
- week 11: polish: 2 min demo video, diagram, small hosted demo if cheap
- week 12 (21 feb 2027): writeup "what broke in my rag agent and how i measured it"

planned corpus is a suggestion only: anthropic, openai and langchain public docs + changelogs. the final pick is a week-1 task.

## rules

- no feature without a metric that moves.
- every claim links to a result file.
- commit daily.

## layout

- `corpus/` - the cleaned corpus, one file per page
- `questions/` - gold questions and gold passages (`gold.jsonl`, schema in `questions/README.md`)
- `retrieval/` - retrievers (bm25 baseline first, dense next)
- `agent/` - the tool loop, state and budgets
- `evals/` - metrics, schema validation and the eval runner
- `runs/` - recorded traces and result json, one file per run

## dev

```
pip install -e ".[dev]"
pytest
python -m evals.run_eval
```
