import json
import logging
import argparse
from pathlib import Path

from app import main
from db import WordDB, TABLES

log = logging.getLogger("main")

parser = argparse.ArgumentParser(description="Database manager", prog="python db.py")
parser.add_argument("-c", "--create", help="Create database", action="store_true")
parser.add_argument("-p", "--purge", help="Purge database", action="store_true")
parser.add_argument("-d", "--dump", help="Dump all records", metavar="dir")
parser.add_argument(
    "-m", "--migrate", help="Migrate old records into database", metavar="dir"
)
parser.add_argument("-v", "--verbose", help="Display messages", action="store_true")

if __name__ == "__main__":
    try:
        db = WordDB()
        args = parser.parse_args()
        verbose = bool(args.verbose)

        if args.create:
            print("Database created")
        elif args.purge:
            cnt = db.purge()
            print(f"{cnt}/{len(TABLES)} table(s) purged")
        elif args.dump:
            path = Path(args.dump)
            if not path.exists():
                path.mkdir(parents=True)
            records = db.dump()
            cnt = 0
            for record in records:
                word = record["word"]
                rp = path / f"{word}.json"
                if rp.write_text(json.dumps(record)) > 0:
                    cnt += 1
                if verbose:
                    print(rp.absolute())
            print(f"{cnt}/{len(records)} record(s) dumped")
        elif args.migrate:
            path = Path(args.migrate)
            records = [json.loads(rp.read_bytes()) for rp in path.iterdir()]
            cnt = db.migrate(records, verbose=verbose)
            print(f"{cnt}/{len(records)} record(s) loaded")
        else:
            main()
    except Exception as e:
        log.warning(f"main: {e}")
