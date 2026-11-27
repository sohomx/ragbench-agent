# retrieval

placeholder. the bm25 baseline lands in week 1 (rank_bm25 or own implementation, deterministic, no network). dense retrieval lands in week 2, then the week-4 ablations (chunk size, overlap, hybrid bm25+dense, reranker).

a retriever takes a question and returns a ranked list of doc ids (later: passage ids), which evals/ scores with recall@k and mrr.
