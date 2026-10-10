"""Plan -> independent workers -> synthesis. Bounded sections and concurrency."""

import json

from common import client, model
from pydantic import BaseModel

from pure_agents.workflows import orchestrate


class Section(BaseModel):
    title: str
    instructions: str
    target_words: int


class Plan(BaseModel):
    sections: list[Section]


plan = client.responses.parse(
    model=model,
    text_format=Plan,
    instructions="Plan exactly three independent sections for a beginner tutorial on tool calling.",
    input="Target 450 words total. Assign a target_words count to each section.",
).output_parsed
if plan is None:
    raise RuntimeError("Missing plan")


def worker(section):
    return client.responses.create(
        model=model,
        instructions="Write only the assigned section. Respect the target word count.",
        input=section.model_dump_json(),
    ).output_text


def reviewer(sections):
    return client.responses.create(
        model=model,
        instructions="Combine these sections, improve transitions, keep factual claims modest.",
        input=json.dumps(sections),
    ).output_text


print(orchestrate(plan.sections, worker, reviewer))
