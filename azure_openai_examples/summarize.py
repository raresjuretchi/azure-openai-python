"""Summarise a local text or Markdown file into key points, as JSON.

    python -m azure_openai_examples.summarize docs/design.md

Uses structured outputs (a JSON schema) so the result can be parsed reliably.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from azure_openai_examples.client import deployment, get_client

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string", "description": "Two or three sentences."},
        "key_points": {"type": "array", "items": {"type": "string"}, "maxItems": 7},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "summary", "key_points", "open_questions"],
    "additionalProperties": False,
}

MAX_CHARS = 200_000


def summarize(client, model: str, text: str) -> dict:
    response = client.responses.create(
        model=model,
        instructions="Summarise the document for a busy architect. Be factual; do not invent details.",
        input=text[:MAX_CHARS],
        text={"format": {"type": "json_schema", "name": "summary", "schema": SCHEMA, "strict": True}},
    )
    return json.loads(response.output_text)


def render(result: dict) -> str:
    lines = [f"# {result['title']}", "", result["summary"], "", "Key points:"]
    lines += [f"  - {p}" for p in result["key_points"]]
    if result["open_questions"]:
        lines += ["", "Open questions:"] + [f"  - {q}" for q in result["open_questions"]]
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python -m azure_openai_examples.summarize <file>")
    text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    print(render(summarize(get_client(), deployment(), text)))


if __name__ == "__main__":
    main()
