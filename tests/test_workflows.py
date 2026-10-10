import asyncio
import unittest

from pure_agents.workflows import chain, orchestrate, parallel_checks, route


class WorkflowTests(unittest.TestCase):
    def test_chain_and_route(self):
        self.assertEqual(chain(2, [lambda n: n + 1, lambda n: n * 3]), 9)
        self.assertEqual(route("list", {"list": str}, 9), "9")
        with self.assertRaises(ValueError):
            route("unknown", {}, 1)

    def test_parallel_checks_fail_closed(self):
        async def yes():
            return True

        async def no():
            return False

        async def broken():
            raise RuntimeError("check failed")

        self.assertFalse(asyncio.run(parallel_checks(yes(), no())))
        with self.assertRaises(RuntimeError):
            asyncio.run(parallel_checks(yes(), broken()))

    def test_orchestration_keeps_order(self):
        self.assertEqual(orchestrate([1, 2, 3], lambda x: x * 2, sum), 12)
        with self.assertRaises(ValueError):
            orchestrate([], str, str)
