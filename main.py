import threading
from queue import Queue
from time import sleep
from collections import namedtuple

from flask import Flask, jsonify, request, render_template

from od_api import process_record
from config import QUERY_INTERVAL

Record = namedtuple("Record", ["word", "context"])
app = Flask(__name__)
records = Queue()


def process_records(interval) -> None:
    global records
    while True:
        if records.empty():
            sleep(interval)
        else:
            word, context = records.get_nowait()
            process_record(word, context)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/word", methods=["POST"])
def post_word():
    data: dict = request.json
    rc, msg = record(data)
    return jsonify({"msg": msg}), rc


def record(data: dict) -> None:
    global records
    try:
        word = data["word"]
        context = data["context"]
    except:
        return (400, "Invalid parameters")
    records.put_nowait(Record(word, context))
    return (200, "Record successfully")


def main() -> None:
    # Start query thread
    threading.Thread(
        target=process_records, kwargs={"interval": QUERY_INTERVAL}
    ).start()
    app.run(host="0.0.0.0", port=21000, debug=False, threaded=True)


if __name__ == "__main__":
    main()
