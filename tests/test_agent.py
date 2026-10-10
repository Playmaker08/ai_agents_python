import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from pure_agents.agent import CalendarAgent
from pure_agents.calendar import CalendarStore
from pure_agents.tools import ToolRegistry


class Item(SimpleNamespace):
    def model_dump(self, **kwargs):
        return vars(self)


def response(items=None, text="", status="completed"):
    return SimpleNamespace(output=items or [], output_text=text, status=status)


def call(name="list_events", arguments="{}", call_id="one"):
    return Item(type="function_call", name=name, arguments=arguments, call_id=call_id)


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.store = CalendarStore(":memory:")
        self.registry = ToolRegistry(self.store)
        self.client = Mock()
        self.agent = CalendarAgent(self.client, "test-model", self.registry)

    def tearDown(self):
        self.store.close()

    def test_no_tool(self):
        self.client.responses.create.return_value = response(text="Hello")
        self.assertEqual(self.agent.run("Hello"), "Hello")
        self.assertEqual(self.store.list_events(), [])

    def test_multiple_tools_and_transcript(self):
        self.client.responses.create.side_effect = [
            response([call(call_id="one"), call("search_kb", '{"question":"conflicts"}', "two")]),
            response(text="No events. Conflicts are rejected."),
        ]
        self.agent.run("Show events and explain conflicts")
        history = self.client.responses.create.call_args.kwargs["input"]
        outputs = [item for item in history if item.get("type") == "function_call_output"]
        self.assertEqual([item["call_id"] for item in outputs], ["one", "two"])
        self.assertEqual(
            sum(
                item.get("call_id") == "one" and item.get("type") == "function_call"
                for item in history
            ),
            1,
        )

    def test_malformed_arguments_return_error(self):
        self.client.responses.create.side_effect = [
            response([call(arguments="{")]),
            response(text="Please retry"),
        ]
        self.agent.run("Show events")
        tool_output = self.agent.history[-1]
        self.assertIn("error", json.loads(tool_output["output"]))

    def test_budget(self):
        self.agent.max_rounds = 2
        self.client.responses.create.return_value = response([call()])
        with self.assertRaisesRegex(RuntimeError, "turn budget"):
            self.agent.run("Loop")
        self.assertEqual(self.client.responses.create.call_count, 2)

    def test_incomplete_response(self):
        self.client.responses.create.return_value = response(status="incomplete")
        with self.assertRaises(RuntimeError):
            self.agent.run("Hello")

    def test_tool_budget(self):
        self.agent.max_calls = 1
        self.client.responses.create.return_value = response([call(), call(call_id="two")])
        with self.assertRaisesRegex(RuntimeError, "Tool call budget"):
            self.agent.run("Hello")
