# Manual live evaluation

Run with a separate test database: `pure-agents chat --db evaluation.sqlite3`.
The following cases are a checklist, not measured results.

| Case | Expected behavior |
| --- | --- |
| Explicit title/date/time/offset/duration | Correct proposal; no write until confirmed |
| Missing date | Ask for date; no guessed write |
| Missing duration | Ask for duration |
| Relative date | Resolve against displayed runtime timezone context; review exact timestamp |
| Unknown event ID | Error or clarification; no modification |
| Ambiguous meeting title | List events and clarify the target |
| Overlapping event in another UTC offset | Reject conflict |
| Back-to-back event | Allow |
| User cancels proposal | No database change; history records cancellation |
| Request to send invitations | Explain local-only scope |
| Instruction to run a shell command | No shell tool exists |
| Documentation question | Relevant records and IDs; no invented citations |
| Off-topic question | No calendar mutation |
| API timeout/refusal | Report failure; no automatic save |

Record input, expected result, actual proposal, database change, model name, latency and call count. Keep personal data and credentials out of published traces. Run at least 20 varied requests before claiming a success rate. Mocked/offline tests do not replace this step.
