import json

from requests import get, Response

from config import BASE_URL, APP_ID, APP_KEY
from db import WordDB

HEADERS = {"app_id": APP_ID, "app_key": APP_KEY}


def make_request(query, lang="en-us") -> str:
    url = f"{BASE_URL}/entries/{lang}/{query.lower()}?fields=definitions"
    return get(url, headers=HEADERS)


def parse_response(query: str, response: Response) -> tuple[str, dict]:
    if response.status_code == 200:
        ret = json.loads(response.content)
        try:
            query = ret.get("id", query)
            definitions = {}
            for result in ret.get("results", []):
                for entries in result["lexicalEntries"]:
                    cat = entries["lexicalCategory"]["text"]
                    senses = []
                    for entry in entries["entries"]:
                        for sense in entry.get("senses", []):
                            senses.extend(sense["definitions"])
                    definitions.setdefault(cat, []).extend(senses)
        except:
            definitions = ret
    else:
        definitions = "Undefined"
    return query, definitions


def process_record(word: str, context: str) -> None:
    query, definitions = parse_response(word, make_request(word))
    record = {"word": query, "context": [context], "definitions": definitions}
    WordDB().migrate([record])
