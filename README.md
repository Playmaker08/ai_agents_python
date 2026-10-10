# Pure Python AI Agents

Build and understand LLM workflows with Python, the OpenAI API, and explicit application logic. No agent framework. Inspired by Dave Ebbelaar's *Building Effective LLM Workflows in Pure Python*.

**Project status: v0.1.0 learning MVP.** Includes eight runnable lessons, a local SQLite Calendar Agent, a bounded tool loop, lexical retrieval, and offline tests. This is a learning project, not a hosted production calendar service.

## Run the offline demo

Python 3.11+ required. No API key or third-party runtime dependency needed for offline mode.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
pure-agents demo
python -m unittest discover -s tests -v
```

The demo prints a proposal, saves a scripted sample event, modifies it, searches the KB, and lists the result. It uses a temporary database and makes **no LLM calls**. It demonstrates execution wiring, not natural-language understanding.

## Run the live agent

```bash
python -m pip install -e '.[live,dev]'
cp .env.example .env
# Edit .env: set your own OPENAI_API_KEY. Never commit it.
pure-agents chat
```

The default model is `gpt-4o` to follow the tutorial. Configure `OPENAI_MODEL` for a model accessible to your API account that supports Responses function calling and structured outputs. API calls incur usage charges; offline demo and tests do not. Live mode requires network access and API credentials. The examples use the Responses API; uploaded tutorial code used Chat Completions.

Try:

> Propose a Bloomberg research meeting on October 13, 2026 at 7 PM America/Indiana/Indianapolis for 45 minutes, with Andy and Alice.

> List my events.

> Move event [use the real ID from the list] to October 14, 2026 at 7 PM in the same timezone.

> Where are events stored? Cite the documentation record.

Each write shows its exact arguments and asks `Save this change? [y/N]`. Only `y` applies it. Success is printed from the database operation. This version sends no emails or invitations.

```bash
pure-agents list --db calendar.sqlite3
```

## Learning sequence

Install `.[live]` for all API examples. Execute from the repo root.

| Lesson | Command | Checkpoint |
| --- | --- | --- |
| Basic call | `python examples/01_basic.py` | Explain input, instructions, and response |
| Structured output | `python examples/02_structured.py` | Identify nullable fields and refusals |
| Tools | `python examples/03_tools.py` | Trace proposal versus persisted event |
| Retrieval | `python examples/04_retrieval.py` | Explain lexical ranking and record IDs |
| Chaining | `python examples/05_prompt_chaining.py` | Extract, validate, describe a draft |
| Routing | `python examples/06_routing.py` | Inspect intent and selected branch |
| Parallelization | `python examples/07_parallelization.py` | Run independent checks concurrently |
| Orchestration | `python examples/08_orchestrator.py` | Inspect plan, workers, synthesis |

Lessons 1-3 and 5-8 use live model calls; lesson 4 is offline. Routing lesson handlers print the branch; the calendar tools perform actual storage operations. Orchestration workers receive explicit section instructions and word targets; generated word counts are not guaranteed.

## Structure

```text
src/pure_agents/
  agent.py       Responses tool loop and session history
  calendar.py    SQLite storage, validation, conflict checks
  tools.py       Allowlist, strict tool schemas, proposals, lexical search
  workflows.py   Chaining, routing, async checks, orchestration
  cli.py         Offline demo and interactive live agent
  kb.json        Packaged documentation records
examples/        Eight self-contained learning entry points
tests/          Offline behavior and mocked API-contract tests
docs/           Architecture, roadmap, evaluation cases
.github/workflows/ci.yml
```

## Verification

```bash
python -m unittest discover -s tests -v
ruff check .
pure-agents demo
```

CI runs on Python 3.11, 3.12, and 3.13 without API credentials. The initial local run passed 20 tests on Python 3.12, Ruff checks and the installed CLI demo. Live API behavior has not been measured.

Mocked tests exercise tool transcripts, malformed JSON, budgets, incomplete responses, proposals, storage and timezone-aware overlaps. They cannot establish live model accuracy or account availability. See [evaluation cases](docs/EVALUATION.md) before relying on the live agent.

## Limits and engineering decisions

- Conversation memory lasts only for the current CLI session; events persist in SQLite.
- Lexical retrieval returns up to three matching records, with no embedding model.
- A self-reported LLM confidence score is not used as proof of correctness.
- All events share a single local calendar; overlaps are blocked regardless of participants.
- Offsets are required. The model resolves relative dates using the configured IANA timezone. Ambiguous or nonexistent DST wall times still need human review.
- Single-user process only: no authentication, concurrent-write coordination, hosted API or external calendar integration.
- Agent loop: at most eight response rounds and sixteen tool calls per request. SDK timeout is 30 seconds, with at most two SDK retries. History grows during a session; no context compaction yet.
- Writes require a registered, reviewed proposal and are revalidated at execution. There is no model-selected shell execution.
- API requests set `store=False`; this setting is not a blanket claim about provider retention policies.
- Tool and retrieved data can still influence model text. Deterministic validation and review protect calendar writes; LLM checks alone are not a security guarantee.

## Publish to GitHub

Create an **empty** repository called `pure-python-ai-agents` in your account. Extract the archive and then:

```bash
git init -b main
git add .
git commit -m "Initial pure Python AI agents learning project"
git remote add origin https://github.com/YOUR_USERNAME/pure-python-ai-agents.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your account. A preconfigured remote is intentionally absent. If using the working checkout, it is already initialized; start at `git remote add origin`.

## Attribution and references

This implementation is newly written for this project. It does not redistribute the uploaded tutorial source or assume its license. Credit for the educational progression goes to Dave Ebbelaar:

- [AI Cookbook workflows](https://github.com/daveebbelaar/ai-cookbook/tree/main/patterns/workflows)
- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

The repository's original code is MIT licensed; upstream tutorial materials remain subject to their own license.
