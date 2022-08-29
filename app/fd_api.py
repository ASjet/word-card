import logging

BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries"

log = logging.Logger("fd_api")


def make_query(word: str, lang: str = "en") -> str:
    return f"{BASE_URL}/{lang}/{word.lower()}"


def parse_response(word: str, resp: dict) -> tuple[str, dict]:
    resp = resp[0]
    query = resp.get("word", word)
    _phonetic = resp.get("phonetic", "")
    definitions = {}
    for meaning in resp.get("meanings", []):
        cat = meaning.get("partOfSpeech", "")
        definitions[cat] = [
            entry["definition"] for entry in meaning.get("definitions", [])
        ]
    return query, definitions
