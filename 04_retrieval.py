"""Offline lexical search with record IDs; this is not vector search."""

from pure_agents.tools import search_kb

for row in search_kb("How are calendar conflicts handled?"):
    print(f"[{row['id']}] {row['answer']}")
