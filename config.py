import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass


QUERY_INTERVAL_DEFAULT = 60
QUERY_INTERVAL = float(os.environ.get("QUERY_INTERVAL", QUERY_INTERVAL_DEFAULT))

BASE_URL = os.environ.get("BASE_URL")
APP_ID = os.environ.get("APP_ID")
APP_KEY = os.environ.get("APP_KEY")
RECORD_ROOT = os.environ.get("RECORD_ROOT", "records")
