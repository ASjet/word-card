from flask import Flask, jsonify, request, render_template, Response

from od_api import process_record
from db import WordDB

app = Flask(__name__)


def json_response(code: int, msg: str, data: dict) -> tuple[Response, int]:
    return jsonify({"msg": msg, "data": data}), code


def record(data: dict) -> None:
    global records
    try:
        word = data["word"]
        context = data["context"]
        process_record(word, context)
        return json_response(200, "Record successfully", None)
    except KeyError:
        return json_response(400, "Invalid parameters", None)
    except ValueError as e:
        return json_response(404, str(e), None)
    except Exception as e:
        return json_response(500, str(e), None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/word", methods=["GET", "POST"])
def post_word():
    if request.method == "GET":
        try:
            db = WordDB()
            words = db.retrive_words()
            return json_response(200, None, words)
        except Exception as e:
            return json_response(500, str(e), None)
    elif request.method == "POST":
        data: dict = request.json
        return record(data)


@app.route("/define", methods=["GET"])
def get_define():
    try:
        word = request.args.get("word")
        db = WordDB()
        record = db.retrive_record(word)
        return json_response(200, None, record)
    except KeyError as e:
        return json_response(400, "Invalid parameters", None)


@app.route("/master", methods=["PUT"])
def master():
    try:
        word = request.args.get("word")
        db = WordDB()
        db.master_word(word)
        return json_response(200, "Marked as mastered", None)
    except KeyError:
        return json_response(400, "Invalid parameters", None)
    except Exception:
        return json_response(500, "Failed to record", None)


def main() -> None:
    app.run(host="0.0.0.0", port=21000, debug=False, threaded=True)
