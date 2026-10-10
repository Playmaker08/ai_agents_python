"""A bounded tool loop. Prompt creates a proposal, never an automatic write."""

from common import client, model

from pure_agents.agent import CalendarAgent
from pure_agents.calendar import CalendarStore
from pure_agents.tools import ToolRegistry

store = CalendarStore(":memory:")
try:
    registry = ToolRegistry(store)
    agent = CalendarAgent(client, model, registry)
    print(
        agent.run(
            "List my events, then propose a 45-minute research meeting on "
            "2026-10-13 at 19:00 America/Indiana/Indianapolis. No participants."
        )
    )
    print("Pending:", registry.pending)
    print("Saved:", store.list_events())
finally:
    store.close()
