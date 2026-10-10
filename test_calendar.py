import unittest

from pure_agents.calendar import CalendarStore, validate_event
from pure_agents.tools import ToolRegistry, search_kb

ARGS = dict(
    title="Research", start="2026-10-13T19:00:00-04:00", duration_minutes=45, participants=["Andy"]
)


class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.store = CalendarStore(":memory:")
        self.registry = ToolRegistry(self.store)

    def tearDown(self):
        self.store.close()

    def test_proposal_does_not_write(self):
        self.registry.execute("propose_create_event", ARGS)
        self.assertEqual(self.store.list_events(), [])
        event = self.registry.apply(self.registry.pending[0])
        self.assertEqual(self.store.list_events()[0]["id"], event["id"])

    def test_conflict_different_offset(self):
        self.store.create_event(**ARGS)
        with self.assertRaises(ValueError):
            self.store.create_event(**{**ARGS, "start": "2026-10-13T23:15:00+00:00"})
        self.assertEqual(len(self.store.list_events()), 1)

    def test_back_to_back(self):
        self.store.create_event(**ARGS)
        self.store.create_event(**{**ARGS, "start": "2026-10-13T19:45:00-04:00"})
        self.assertEqual(len(self.store.list_events()), 2)

    def test_modify_persists(self):
        event = self.store.create_event(**ARGS)
        updated = self.store.modify_event(event["id"], **{**ARGS, "title": "Updated"})
        self.assertEqual(updated["title"], "Updated")
        self.assertEqual(self.store.list_events()[0]["title"], "Updated")

    def test_invalid_date_duration_participants(self):
        for update in [
            {"start": "2026-10-13T19:00:00"},
            {"duration_minutes": 0},
            {"duration_minutes": True},
            {"participants": "Andy"},
            {"title": ""},
        ]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                validate_event(**{**ARGS, **update})

    def test_unknown_tool_and_extra_arguments(self):
        for name, arguments in [("shell", {}), ("list_events", {"extra": 1})]:
            with self.assertRaises(ValueError):
                self.registry.execute(name, arguments)

    def test_unknown_id(self):
        with self.assertRaises(ValueError):
            self.registry.execute("propose_modify_event", {"event_id": "missing", **ARGS})

    def test_retrieval(self):
        self.assertEqual(search_kb("conflicts")[0]["id"], 3)
        self.assertEqual(search_kb("xyzabc"), [])

    def test_apply_rechecks_conflicts(self):
        self.registry.execute("propose_create_event", ARGS)
        self.store.create_event(**ARGS)
        with self.assertRaises(ValueError):
            self.registry.apply(self.registry.pending[0])

    def test_sql_input_is_data(self):
        self.store.create_event(**{**ARGS, "title": "'); DROP TABLE events; --"})
        self.assertEqual(len(self.store.list_events()), 1)
