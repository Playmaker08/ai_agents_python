# Contributing

Use Python 3.11+. Install `pip install -e '.[live,dev]'` in a virtual environment.
Run `python -m unittest discover -s tests -v` and `ruff check .` before proposing changes.
Keep tests offline. Never commit API keys, .env files, databases or private transcripts.
Use narrowly scoped tools; distinguish proposals from completed operations.
