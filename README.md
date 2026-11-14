# AI System Design Playbook

**Real AI systems, designed step by step, in plain English.** Twenty detailed case studies: support agents, WhatsApp bots, voice agents, RAG at scale, coding agents, and more. Each one covers the numbers, the architecture, how it breaks, how it scales, and what it costs.

Free, open source, and written for engineers who want to understand how production AI systems are really built.

> [!NOTE]
> **Part 2 of 2.** The [AI Engineering Playbook](https://github.com/NeuralSaasAi/ai-engineering-playbook) (Part 1) teaches the concepts, from zero to intermediate. This playbook (Part 2) shows how those concepts combine into real systems, with scale, trade-offs and failure modes. New to embeddings, RAG or tool calling? Start with Part 1, then come back.

## I want to

| I want to... | Go to |
|---|---|
| Learn a method I can reuse on any AI design problem | [How to design any AI system](DESIGN-METHOD.md) |
| See how a support, WhatsApp or voice agent is built | [Conversational and voice](#conversational-and-voice) |
| Build RAG that works for many customers and many documents | [Retrieval and search](#retrieval-and-search) |
| Understand how coding agents and research agents work | [Agents](#agents) |
| Run AI on my own GPUs, or control cost across many apps | [Platform and scale](#platform-and-scale) |
| Prepare for an AI system design interview | Every case study has an "Interview mode" section with a timed walkthrough and follow-up questions |
| Write a case study | [CONTRIBUTING.md](CONTRIBUTING.md) |

## How each case study works

Every case study uses the same 17 sections, so you always know where to look. Each section starts with two or three plain sentences, then goes deep.

| You will find | What it gives you |
|---|---|
| The scenario and requirements | A made-up company with real-sized numbers, and what "good" means |
| Numbers | Back-of-envelope math with every formula shown |
| Choosing the shape | Why a simple pipeline, a router, or an agent |
| Architecture and one request, end to end | Diagrams and a latency budget |
| Deep dives | The three or four hardest parts, with the options we weighed |
| Scaling from 1x to 100x | What breaks first and how to fix it |
| Failure modes and safety | How it fails and what you do about it |
| Measuring quality and cost | Metrics, release gates, cost per unit of work |
| Interview mode | A 45-minute plan and follow-up questions with answers |

The scenarios are fictional, so numbers are illustrative. Prices appear only as stated assumptions inside the cost formulas, so the math stays useful when vendor prices change.

## Case studies

Status: 📝 planned, 🚧 draft, ✅ reviewed. Want one? See [Contributing](CONTRIBUTING.md).

### Conversational and voice

| # | Case study | Problem | Key patterns | Status |
|---|---|---|---|---|
| 1 | [Customer support agent with human handoff](case-studies/01-customer-support-agent.md) | A small-business software company answers 500K conversations a month | Model cascade, grounded answers, signal-based escalation, safe tools, warm handoff | 🚧 Draft |
| 2 | WhatsApp commerce and support agent | An Indian D2C brand handles 2M chats a month in Hindi, English and Hinglish | 24-hour message window, templates, webhooks, idempotency, human handoff | 📝 Planned |
| 3 | Real-time voice agent for a call center | 5,000 calls at once, each turn answered in under 800 ms | Streaming speech and language models, turn detection, barge-in, telephony | 📝 Planned |
| 11 | Clinical voice scribe | 2,000 clinicians dictate visit notes | Ambient audio, health-data rules, grounded notes, clinician sign-off | 📝 Planned |
| 18 | ChatGPT-style consumer assistant | 10M daily users chat with memory | Streaming, conversation storage, long-term memory, abuse limits | 📝 Planned |
| 19 | AI tutor for Indian students | 1M students at a very low cost per student | Multilingual, safety for minors, adaptive practice, cheap model routing | 📝 Planned |

### Retrieval and search

| # | Case study | Problem | Key patterns | Status |
|---|---|---|---|---|
| 4 | Enterprise knowledge assistant | 10,000 employees search 2M documents in 15 systems | Permission-aware retrieval, incremental sync, citations, honest "I don't know" | 📝 Planned |
| 5 | Multi-tenant RAG SaaS | 5,000 customers share one platform | Tenant isolation, noisy neighbors, per-tenant quotas and indexes | 📝 Planned |
| 6 | AI answer engine | 1M questions a day answered from the live web | Search plus crawl, fresh index, citations, answer caching | 📝 Planned |
| 10 | Document intelligence pipeline | 50K contracts and invoices a month | Vision models, parallel extractors, human review queue, batch jobs | 📝 Planned |

### Agents

| # | Case study | Problem | Key patterns | Status |
|---|---|---|---|---|
| 7 | How a coding agent works | From one developer to 10,000 seats | Agent loop, tools, sandbox, code index, context compaction, sub-agents | 📝 Planned |
| 8 | Deep research agent | 20,000 jobs a day, each running 30 minutes | Planner and workers, durable execution, token budgets, source checking | 📝 Planned |
| 9 | Text-to-SQL analytics agent | 500 analysts, 3,000 tables | Schema retrieval, query validation, read-only access, row-level security | 📝 Planned |
| 14 | Back-office computer-use agent | Expense reports across three legacy screens | VM sandbox, approval gate, prompt-injection defense | 📝 Planned |

### Trust and safety

| # | Case study | Problem | Key patterns | Status |
|---|---|---|---|---|
| 12 | Content moderation at scale | 50M posts a day | Cheap-to-expensive classifier cascade, policy as prompt, appeals | 📝 Planned |
| 13 | Fraud detection with explanations | A decision in 100 ms at 10K transactions a second | ML and rules on the hot path, language model explanations off it | 📝 Planned |

### Platform and scale

| # | Case study | Problem | Key patterns | Status |
|---|---|---|---|---|
| 15 | Company AI gateway and model router | 200 internal apps share model access | Token-based rate limits, fallback, cost attribution, semantic cache | 📝 Planned |
| 16 | Self-hosted LLM inference platform | Open models serving 5,000 requests a second | Continuous batching, KV cache, prefix-aware routing, GPU autoscaling | 📝 Planned |
| 17 | Eval-gated CI/CD for LLM features | 40 prompts and agents in production | Golden sets, LLM judges, regression gates, canary releases | 📝 Planned |

### Industry

| # | Case study | Problem | Key patterns | Status |
|---|---|---|---|---|
| 20 | Manufacturing defect and maintenance copilot | 12 plants, edge cameras, 30 years of manuals | Vision at the edge, retrieval over manuals plus sensor data, offline mode | 📝 Planned |

More are coming: MCP knowledge agents, multi-tenant fine-tuning, distillation to cut cost, recommendation explanations, compliance pre-screening, meeting summarizers, and energy-efficiency advisors. [Suggest one](https://github.com/NeuralSaasAi/ai-system-design-playbook/issues/new?template=propose-case-study.yml).

## Questions people ask

**What is AI system design?**
It is the work of designing everything around an AI model so it serves real users: how requests flow, where data comes from, how it stays fast, safe and affordable, and how you know it is working.

**How is this different from the AI Engineering Playbook?**
Part 1 teaches the building blocks and is written for beginners up to intermediate. Part 2 assumes you know the blocks and shows how they fit together at scale.

**Is it useful for interviews?**
Yes. Each case study includes a timed walkthrough and follow-up questions. The [design method](DESIGN-METHOD.md) gives you a repeatable way to structure any answer.

**Is it free? Can I contribute?**
Yes to both. Read [CONTRIBUTING.md](CONTRIBUTING.md), then claim a planned case study or fix something you find.

## Contribute

Found a mistake, want a case study, or have a production story to share? [Open an issue](https://github.com/NeuralSaasAi/ai-system-design-playbook/issues/new/choose) or send a pull request. Small fixes help as much as big ones. Star the repo to follow new case studies as they land.

Read our [style guide](STYLE.md) before writing, and the [Code of Conduct](CODE_OF_CONDUCT.md) before joining in.

## Why this exists

[Why we built this](WHY-THIS-EXISTS.md)

## License

Content is licensed under [CC BY-SA 4.0](LICENSE). Maintained by [NeuralSaaS](https://github.com/NeuralSaasAi).
