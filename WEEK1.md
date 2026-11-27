# week 1

- [ ] pick the corpus (suggestion: anthropic, openai, langchain public docs + changelogs); write down why and the license/terms check in corpus/README.md
- [ ] scrape and clean it into corpus/ (one file per page, stable ids, source url + fetch date in a header)
- [ ] write 30 gold questions with gold passages in questions/gold.jsonl (schema in questions/README.md); mix of lookup, multi-passage, and a few unanswerable ones
- [ ] baseline BM25 retrieval in retrieval/ (rank_bm25 or own implementation), deterministic, no network
- [ ] first recall@k number: run evals, fill the first row of the README results table, commit the result json in runs/

done when: README table has one real row linking to a file in runs/.
