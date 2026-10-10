"""Validated local calendar storage. Every mutation is an explicit Python action."""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from uuid import uuid4


def validate_event(title, start, duration_minutes, participants):
    if not isinstance(title, str) or not title.strip() or len(title) > 200:
        raise ValueError("title must contain 1-200 characters")
    if not isinstance(start, str):
        raise ValueError("start must be an ISO 8601 string")
    dt = datetime.fromisoformat(start)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("start must include a UTC offset")
    if type(duration_minutes) is not int or not 1 <= duration_minutes <= 1440:
        raise ValueError("duration_minutes must be an integer from 1 to 1440")
    if not isinstance(participants, list) or not all(
        isinstance(p, str) and p.strip() for p in participants
    ):
        raise ValueError("participants must be a list of nonempty strings")
    return {
        "title": title.strip(),
        "start": dt.isoformat(),
        "duration_minutes": duration_minutes,
        "participants": participants,
    }


class CalendarStore:
    def __init__(self, path="calendar.sqlite3"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, start TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL, participants TEXT NOT NULL)""")
        self.db.commit()

    def close(self):
        self.db.close()

    def list_events(self):
        events = [dict(row) for row in self.db.execute("SELECT * FROM events")]
        for event in events:
            event["participants"] = json.loads(event["participants"])
        return sorted(events, key=lambda e: datetime.fromisoformat(e["start"]))

    def _conflicts(self, event, exclude=None):
        start = datetime.fromisoformat(event["start"]).astimezone(UTC)
        end = start + timedelta(minutes=event["duration_minutes"])
        for other in self.list_events():
            if other["id"] == exclude:
                continue
            other_start = datetime.fromisoformat(other["start"]).astimezone(UTC)
            other_end = other_start + timedelta(minutes=other["duration_minutes"])
            if start < other_end and other_start < end:
                raise ValueError(f"Event conflicts with {other['id']}: {other['title']}")

    def create_event(self, title, start, duration_minutes, participants):
        event = validate_event(title, start, duration_minutes, participants)
        self._conflicts(event)
        event_id = uuid4().hex[:12]
        with self.db:
            self.db.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                (
                    event_id,
                    event["title"],
                    event["start"],
                    event["duration_minutes"],
                    json.dumps(event["participants"]),
                ),
            )
        return {"id": event_id, **event}

    def modify_event(self, event_id, title, start, duration_minutes, participants):
        if not any(e["id"] == event_id for e in self.list_events()):
            raise ValueError("Event ID not found; list events first")
        event = validate_event(title, start, duration_minutes, participants)
        self._conflicts(event, exclude=event_id)
        with self.db:
            self.db.execute(
                """UPDATE events SET title=?, start=?, duration_minutes=?,
                participants=? WHERE id=?""",
                (
                    event["title"],
                    event["start"],
                    event["duration_minutes"],
                    json.dumps(event["participants"]),
                    event_id,
                ),
            )
        return {"id": event_id, **event}
