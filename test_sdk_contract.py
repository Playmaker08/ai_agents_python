"""Exercise the installed OpenAI SDK against a local HTTP mock, never the network."""

import importlib.util
import json
import unittest

from pure_agents.agent import CalendarAgent
from pure_agents.calendar import CalendarStore
from pure_agents.tools import ToolRegistry


@unittest.skipUnless(importlib.util.find_spec("openai"), "optional live SDK not installed")
class SDKContractTests(unittest.TestCase):
    def test_responses_tool_transcript(self):
        import httpx
        from openai import OpenAI

        requests = []

        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            output = (
                [
                    {
                        "type": "function_call",
                        "id": "fc_1",
                        "name": "list_events",
                        "call_id": "call_1",
                        "arguments": "{}",
                        "status": "completed",
                    }
                ]
                if len(requests) == 1
                else [
                    {
                        "type": "message",
                        "id": "msg_1",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "Your calendar is empty.",
                                "annotations": [],
                            }
                        ],
                    }
                ]
            )
            return httpx.Response(
                200,
                json={
                    "id": "resp_1",
                    "object": "response",
                    "created_at": 1,
                    "status": "completed",
                    "model": "gpt-4o",
                    "output": output,
                    "error": None,
                    "incomplete_details": None,
                },
            )

        store = CalendarStore(":memory:")
        with OpenAI(
            api_key="offline-test-placeholder",
            max_retries=0,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        ) as client:
            try:
                agent = CalendarAgent(client, "gpt-4o", ToolRegistry(store))
                self.assertEqual(agent.run("List events"), "Your calendar is empty.")
                self.assertEqual(len(requests), 2)
                self.assertFalse(requests[0]["store"])
                self.assertEqual(requests[1]["input"][-1]["call_id"], "call_1")
                self.assertEqual(json.loads(requests[1]["input"][-1]["output"]), [])
            finally:
                store.close()
