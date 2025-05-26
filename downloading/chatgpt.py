from __future__ import annotations

import json
import os

from openai import OpenAI

CACHE_FILE = "authors.json"


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rt", encoding="utf-8") as inp:
            return json.load(inp)
    return {}


def save_cache(data: dict):
    with open(CACHE_FILE, "wt", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=4)


TOKEN = os.environ.get("OPENAI_TOKEN")

prompt = (
    "If given person does not exists or is not writer, return 0. "
    "Calculate the probability that the person is from Portugal or Brazil and return (1 if the person is from Portugal or Brazil and 0 if from another country)."
)

schema = {
    "name": "portuguese_author_detector",
    "schema": {
        "type": "object",
        "properties": {
            "probability": {
                "type": "number",
                "description": "Probability whether author is from Portugal or Brazil",
            }
        },
        "required": ["probability"],
        "additionalProperties": False,
    },
    "strict": True,
}


def process_request_impl(author: str) -> dict | None:
    client = OpenAI(
        api_key=TOKEN,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": prompt}]},
            {"role": "user", "content": [{"type": "text", "text": f"Name: {author}"}]},
        ],
        temperature=1,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_schema", "json_schema": schema},
    )

    choices = response.choices

    if len(choices) == 0:
        return None

    if len(choices) > 1:
        return None

    result = json.loads(response.choices[0].message.content)

    return result


cache = load_cache()


def process_request(author: str) -> float:
    author = author.lower().strip()

    if len(author) == 0:
        return False

    if author in cache:
        return cache[author]

    result = process_request_impl(author)
    if result is None or "probability" not in result:
        return False

    cache[author] = result["probability"]
    save_cache(cache)

    return result["probability"]
