import os
import logging
from requests import get, Response

try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass

API_ID = os.environ.get("API_ID")
API_KEY = os.environ.get("API_KEY")
RECORD_ROOT = os.environ.get("RECORD_ROOT", "records")

BASE_URL = "https://od-api.oxforddictionaries.com/api/v2/entries"
HEADERS = {"Accept": "application/json", "app_id": API_ID, "app_key": API_KEY}

log = logging.Logger("od_api")


def make_query(word: str, lang: str = "en-us") -> Response:
    url = f"{BASE_URL}/{lang}/{word.lower()}?fields=definitions"
    return get(url, headers=HEADERS)


def parse_response(word: str, resp: dict) -> tuple[str, dict]:
    query = resp.get("id", word)
    definitions = {}
    for result in resp.get("results", []):
        for entries in result["lexicalEntries"]:
            cat = entries["lexicalCategory"]["text"]
            senses = []
            for entry in entries["entries"]:
                for sense in entry.get("senses", []):
                    senses.extend(sense["definitions"])
            definitions.setdefault(cat, []).extend(senses)
    return query, definitions
