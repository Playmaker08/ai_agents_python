"""Small composable patterns. The model proposes; Python controls execution."""

import asyncio
from concurrent.futures import ThreadPoolExecutor


def chain(value, steps):
    for step in steps:
        value = step(value)
    return value


def route(kind, handlers, value):
    if kind not in handlers:
        raise ValueError(f"Unsupported route: {kind}")
    return handlers[kind](value)


async def parallel_checks(*checks):
    # Any exception prevents acceptance. These are independent checks only.
    results = await asyncio.gather(*checks)
    return all(results)


def orchestrate(plan, worker, reviewer, max_workers=3):
    if not plan or len(plan) > 12:
        raise ValueError("Plan must contain 1-12 independent sections")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        sections = list(pool.map(worker, plan))
    return reviewer(sections)
