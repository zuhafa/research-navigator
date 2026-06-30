install:
	uv sync

playground:
	uv run uvicorn app.custom_server:app --host 127.0.0.1 --port 18081

run:
	uv run python app/agent_runtime_app.py

test:
	uv run pytest
