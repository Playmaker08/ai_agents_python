from typing import Literal

from common import client, model
from pydantic import BaseModel

from pure_agents.workflows import route


class Intent(BaseModel):
    kind: Literal["create", "modify", "list", "other"]


intent = client.responses.parse(
    model=model,
    text_format=Intent,
    instructions="Classify the calendar request.",
    input="Show all my meetings.",
).output_parsed
if intent is None:
    raise RuntimeError("No route extracted")
handlers = {
    kind: (lambda text, k=kind: f"Selected handler: {k}; input: {text}")
    for kind in ["create", "modify", "list", "other"]
}
print(route(intent.kind, handlers, "Show all my meetings."))
# Teaching example: handlers report their branch; real handlers live in tools.py.
