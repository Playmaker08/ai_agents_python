from common import client, model
from pydantic import BaseModel

from pure_agents.calendar import validate_event


class EventDetails(BaseModel):
    title: str
    start: str
    duration_minutes: int
    participants: list[str]


parsed = client.responses.parse(
    model=model,
    text_format=EventDetails,
    instructions="Extract the explicit event details. Do not claim it has been saved.",
    input="Bloomberg meeting on 2026-10-13 at 19:00 UTC-04:00, 45 minutes, with Andy.",
).output_parsed
if parsed is None:
    raise RuntimeError("No event extracted")
validated = validate_event(**parsed.model_dump())
confirmation = client.responses.create(
    model=model,
    instructions="Describe this event draft for review. It has not been saved.",
    input=parsed.model_dump_json(),
)
print(validated)
print(confirmation.output_text)
