from common import client, model
from pydantic import BaseModel


class EventDraft(BaseModel):
    title: str
    start: str | None
    duration_minutes: int | None
    participants: list[str]


response = client.responses.parse(
    model=model,
    text_format=EventDraft,
    instructions="Extract event information. Unknown fields must be null; do not guess dates.",
    input="Bloomberg team meeting with Andy and Alice, 45 minutes; date not decided yet.",
)
if response.output_parsed is None:
    raise RuntimeError("No parsed output: check refusal or incomplete response")
print(response.output_parsed.model_dump_json(indent=2))
