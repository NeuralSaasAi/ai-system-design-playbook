# Style guide

This playbook teaches people how real AI systems are designed and scaled. Every rule below serves that goal. It follows the same spirit as the [AI Engineering Playbook](https://github.com/NeuralSaasAi/ai-engineering-playbook) style guide.

## Who we write for

An engineer who has used an LLM API and knows the basics (tokens, embeddings, RAG). If a reader needs those basics, they go to Part 1 and come back. Part 2 starts where Part 1 stops.

A beginner should be able to follow the first paragraph of every section. A senior engineer should still learn something from the last paragraph.

## How a case study is built

Every case study uses [templates/case-study-template.md](templates/case-study-template.md). The 17 sections are fixed and in order. `scripts/check_case_studies.py` enforces the structure, so CI fails if a section is missing or out of order.

Each section follows the same shape:

1. Open with two or three plain sentences that say what this section decides and why.
2. Then go deep: tables, diagrams, numbers, code.

The checker rejects a section that opens with a table, list or code block (except `At a glance`).

## Writing rules

- **Simple English.** Short sentences. One idea per sentence. Active voice. Say "use" instead of "utilize" and "start" instead of "initiate".
- **Technical terms are fine, jargon is not.** Use the term engineers actually use (KV cache, p95 latency), and explain it in one sentence the first time it appears. Don't invent labels or stack acronyms.
- **Link, don't re-teach.** If Part 1 explains a concept, link to it. Don't write the lesson again.
- **Show the math.** Every number in a case study comes from a formula shown on the page, with its assumptions. A reader should be able to change an assumption and redo the math.
- **Describe things at real size.** No "revolutionary", "robust", "leverage", "delve", "landscape", "pivotal" or "foster". The checker blocks these words outside code.
- **Name the mechanism.** "A cache keyed on the first 2,000 tokens of the prompt" beats "smart caching".
- **Original writing.** Reference repos, books and courses can inspire which topics we cover. Never copy their text, structure, diagrams or code. Short quotes (under 30 words) are fine when marked and cited.
- **No promotion.** No course, product, mentoring or affiliate links in case studies. Tools are named because readers will meet them at work.

## Scenarios are fictional, and say so

Case studies use made-up companies with stated numbers ("a D2C brand with 2M chats a month"). Always say the scenario is illustrative. Never present invented numbers as measurements of a real company.

## Numbers, prices and dates

- Cost formulas use a placeholder price that you state as an assumption, for example "assume $X per 1M input tokens". If you quote a real price, give the vendor page and the month you checked it ("as of November 2026").
- Do not write model leaderboards or price tables. They go stale in weeks. Teach how to calculate, not what the current price is.
- Every case study has a `last_reviewed` date in its front matter. Update it when you re-check facts.

## Sources

Good sources, in order of preference:

1. Official documentation and standards (vendor docs, RFCs, regulation text).
2. Original research papers and engineering blogs from the team that built the thing.
3. Reputable reporting with named sources.

Every factual claim that might change (limits, prices, dates, versions) needs a link. When a popular claim can't be verified, leave it out. Don't repeat it with a disclaimer.

## Code in case studies

- Short (under about 30 lines) and vendor-neutral. Show the idea (a routing function, a token budget, a permission filter), not a full SDK integration.
- Python by default. Never put a real API key in an example.
- Name the real tool in prose when it helps ("Redis", "Postgres with pgvector"). Keep the code readable without that tool.

## Formatting

The same files are read on github.com and may be built into a website later. Use only features that render in both places.

| Need | Use | Don't use |
|---|---|---|
| Side notes and warnings | GitHub alerts: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]` | `!!! note` (MkDocs) or `{: .note}` (Jekyll) |
| Diagrams | Code fences marked `mermaid` | Screenshots or ASCII art for diagrams |
| Hidden answers | `<details><summary>Answer</summary> ... </details>`, with a blank line after `<summary>` | Custom widgets |
| Links between pages | Relative paths to `.md` files, for example `02-whatsapp-agent.md` | Absolute website URLs |
| Everything else | GitHub-flavored markdown: tables, code fences, task lists | Shortcodes, Liquid tags, HTML layouts |

Front matter has five fields:

```yaml
---
title: Customer support agent with human handoff
level: advanced          # intermediate | advanced
status: reviewed         # planned | draft | reviewed
category: Conversational and support
last_reviewed: 2026-11-14
---
```

## Status levels

| Status | Meaning |
|---|---|
| 📝 `planned` | Listed in the catalog. Front matter only. Someone may claim it. |
| 🚧 `draft` | Content exists but is not fully checked. All template rules apply. |
| ✅ `reviewed` | At least 2,500 words, at least two mermaid diagrams, sources checked, and a second person has read it. |
