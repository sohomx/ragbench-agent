# corpus

the cleaned corpus lives here. nothing yet: picking the corpus is a week-1 task (see ../WEEK1.md).

## what goes here

- one file per source page, cleaned to plain text or markdown.
- a short note in this file on why this corpus was picked and the license/terms check.

## file naming

- `<source>/<doc_id>.md`, e.g. `anthropic/anthropic-docs-0001.md`.
- `doc_id` is stable: once assigned it never changes, because questions/gold.jsonl points at it.

## header format

every file starts with a small header, then a blank line, then the text:

```
---
doc_id: anthropic-docs-0001
source_url: https://example.com/page
fetched: 2026-11-30
---
```

gold passage offsets (`start_char`, `end_char`) are measured on the text after the header.
