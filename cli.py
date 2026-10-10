"""CLI and a deterministic offline integration demo."""

import argparse
import json
import os
import tempfile

from .calendar import CalendarStore
from .tools import ToolRegistry, search_kb


def demo():
    with tempfile.TemporaryDirectory() as directory:
        store = CalendarStore(f"{directory}/demo.sqlite3")
        registry = ToolRegistry(store)
        args = {
            "title": "Bloomberg team research meeting",
            "start": "2026-10-13T19:00:00-04:00",
            "duration_minutes": 45,
            "participants": ["Andy", "Alice", "Bob"],
        }
        print("OFFLINE DEMO: scripted tools, no LLM calls, temporary database")
        print(json.dumps(registry.execute("propose_create_event", args), indent=2))
        event = registry.apply(registry.pending[0])
        print("Saved:", json.dumps(event))
        modified = {**args, "event_id": event["id"], "start": "2026-10-14T19:00:00-04:00"}
        registry.execute("propose_modify_event", modified)
        print("Modified:", json.dumps(registry.apply(registry.pending[0])))
        print("Retrieval:", json.dumps(search_kb("Where are calendar events stored?")))
        print("Stored events:", json.dumps(store.list_events()))
        store.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo", "chat", "list"])
    parser.add_argument("--db", default=None)
    args = parser.parse_args()
    if args.command == "demo":
        demo()
        return
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    store = CalendarStore(args.db or os.getenv("AGENT_DB", "calendar.sqlite3"))
    try:
        if args.command == "list":
            print(json.dumps(store.list_events(), indent=2))
            return
        if not os.getenv("OPENAI_API_KEY"):
            parser.error("Set OPENAI_API_KEY; use 'demo' for offline mode")
        try:
            from openai import OpenAI
        except ImportError:
            parser.error("Install live dependencies: pip install -e '.[live]'")
        from .agent import CalendarAgent

        registry = ToolRegistry(store)
        agent = CalendarAgent(
            OpenAI(timeout=30, max_retries=2),
            os.getenv("OPENAI_MODEL", "gpt-4o"),
            registry,
            os.getenv("AGENT_TIMEZONE", "America/Indiana/Indianapolis"),
        )
        print("Local calendar agent. Type 'exit' to stop. Writes require confirmation.")
        while True:
            try:
                text = input("You> ")
            except EOFError:
                break
            if text.strip().lower() in {"exit", "quit"}:
                break
            try:
                print("Agent>", agent.run(text))
                for proposal in list(registry.pending):
                    print(json.dumps(proposal, indent=2))
                    if input("Save this change? [y/N] ").strip().lower() == "y":
                        result = registry.apply(proposal)
                        agent.record_execution({"status": "saved", "event": result})
                        print("Saved:", json.dumps(result))
                    else:
                        registry.pending.remove(proposal)
                        agent.record_execution({"status": "cancelled", "proposal": proposal})
                        print("Cancelled.")
            except Exception as exc:
                # Do not print provider error bodies, request data, or credentials.
                print(f"Request failed ({type(exc).__name__}). No pending change was auto-saved.")
    finally:
        store.close()


if __name__ == "__main__":
    main()
