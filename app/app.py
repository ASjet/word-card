import os
import json
import logging

from requests import get, Response
from flask import Flask, jsonify, request, render_template, Response

from fd_api import make_query, parse_response
from db import WordDB

QUERY_INTERVAL_DEFAULT = 60
QUERY_INTERVAL = float(os.environ.get("QUERY_INTERVAL", QUERY_INTERVAL_DEFAULT))

app = Flask(__name__)
log = logging.Logger("app")


def query(word: str) -> tuple[str, dict]:
    url = make_query(word)
    resp = get(url)
    if resp.status_code != 200:
        if resp.status_code == 404:
            raise ValueError(json.loads(resp.content))
        else:
            raise ConnectionError(f"get({resp.url}): {resp.status_code} {resp.reason}")
    return parse_response(word, json.loads(resp.content))


def json_response(code: int, msg: str, data: dict) -> tuple[Response, int]:
    return jsonify({"msg": msg, "data": data}), code


def record(data: dict) -> None:
    try:
        word = data["word"]
        context = data["context"]
        res, definitions = query(word)
        WordDB().migrate(
            [
                {
                    "word": res,
                    "mastered": False,
                    "context": [context],
                    "definitions": definitions,
                }
            ]
        )
        return json_response(200, "Record Successfully", None)
    except KeyError as e:
        log.warning(e)
        return json_response(400, "Invalid Parameters", None)
    except ValueError as e:
        log.warning(e)
        return json_response(404, f"Undefined Word: {word}", None)
    except Exception as e:
        log.warning(e)
        return json_response(500, "Internal Error", None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/word", methods=["GET", "POST", "DELETE"])
def api_word():
    if request.method == "GET":
        try:
            db = WordDB()
            words = db.retrive_words()
            return json_response(200, None, words)
        except Exception as e:
            log.warning(e)
            return json_response(500, str(e), None)
    elif request.method == "POST":
        data: dict = request.json
        log.info(f"payload: {data}")
        return record(data)
    elif request.method == "DELETE":
        try:
            log.info(f"payload: {request.args}")
            word = request.args.get("word")
            db = WordDB()
            db.delete_word(word)
            return json_response(200, "Delete successfully", None)
        except KeyError as e:
            log.warning(e)
            return json_response(400, "Invalid parameters", None)
        except Exception:
            log.warning(e)
            return json_response(500, f"Failed to delete word {word}", None)


@app.route("/define", methods=["GET"])
def get_define():
    try:
        log.info(f"payload: {request.args}")
        word = request.args.get("word")
        db = WordDB()
        record = db.retrive_record(word)
        return json_response(200, None, record)
    except KeyError as e:
        log.warning(e)
        return json_response(400, "Invalid parameters", None)


@app.route("/master", methods=["PUT"])
def master():
    try:
        log.info(f"payload: {request.args}")
        word = request.args.get("word")
        db = WordDB()
        db.master_word(word)
        return json_response(200, "Marked as mastered", None)
    except KeyError as e:
        log.warning(e)
        return json_response(400, "Invalid parameters", None)
    except Exception as e:
        log.warning(e)
        return json_response(500, "Failed to record", None)


def main() -> None:
    app.run(host="0.0.0.0", port=21000, debug=False, threaded=True)
