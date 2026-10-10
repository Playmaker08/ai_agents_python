import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

from pure_agents.workflows import parallel_checks


class Check(BaseModel):
    passed: bool
    reason: str


async def main():
    load_dotenv()
    async with AsyncOpenAI(timeout=30, max_retries=2) as client:

        async def check(instruction):
            response = await client.responses.parse(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                text_format=Check,
                instructions=instruction,
                input="Schedule a 45-minute research meeting on October 13, 2026 at 19:00 UTC-04:00.",
            )
            if response.output_parsed is None:
                raise RuntimeError("Missing check result")
            return response.output_parsed.passed

        passed = await parallel_checks(
            check("Check that this is a calendar request."),
            check("Check that an explicit date, time, timezone and duration are provided."),
        )
        print("Both checks passed:", passed)


# LLM checks supplement deterministic validation; they are not security boundaries.
if __name__ == "__main__":
    asyncio.run(main())
