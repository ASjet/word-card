import logging
import sqlite3
from pathlib import Path
from datetime import datetime
import traceback

WORD_DB = "../words.db"
TABLES = ["words", "context", "define", "mastered"]
log = logging.getLogger("sqlite3")


def cur_utc_timestamp() -> int:
    utc_time = datetime.utcnow()
    return int(utc_time.timestamp())


class WordDB:
    DB_NAME = WORD_DB

    def __init__(self):
        if not Path(self.DB_NAME).exists():
            self.init_db()
        else:
            self.con = sqlite3.connect(self.DB_NAME)
            self.cur = self.con.cursor()
        # Turn on foreign key to support on delete cascade
        self.cur.execute("PRAGMA foreign_keys = ON")

    def __del__(self):
        self.con.commit()
        self.con.close()

    def init_db(self):
        try:
            self.con = sqlite3.connect(self.DB_NAME)
            self.cur = self.con.cursor()
            self.cur.execute("PRAGMA foreign_keys = ON")
            sql = """
            CREATE TABLE words (
                id INTEGER PRIMARY KEY,
                word VARCHAR(30) UNIQUE,
                create_time INTEGER
            ) """
            self.cur.execute(sql)
            sql = """
            CREATE TABLE context (
                id INTEGER PRIMARY KEY,
                word INTEGER,
                context VARCHAR(256),
                create_time INTEGER,
                FOREIGN KEY (word) REFERENCES words (id) ON DELETE CASCADE
            )
            """
            self.cur.execute(sql)
            sql = """
            CREATE TABLE define (
                id INTEGER PRIMARY KEY,
                word INTEGER ,
                category VARCHAR(30),
                define VARCHAR(512),
                create_time INTEGER,
                FOREIGN KEY (word) REFERENCES words (id) ON DELETE CASCADE
            )
            """
            self.cur.execute(sql)
            sql = """
            CREATE TABLE mastered (
                id INTEGER PRIMARY KEY,
                word INTEGER ,
                mastered INTEGER DEFAULT FALSE,
                update_time INTEGER,
                FOREIGN KEY (word) REFERENCES words (id) ON DELETE CASCADE
            )
            """
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            log.warning(e, sql)

    def _gen_cond(self, cond: dict) -> str:
        if bool(cond):
            return "WHERE " + ",".join([f'"{k}"="{v}"' for k, v in cond.items()])
        else:
            return ""

    def _insert(self, table: str, fields: dict) -> None:
        columns = []
        values = []
        for k, v in fields.items():
            columns.append(k)
            values.append(f'"{v}"')
        sql = f'INSERT INTO {table} ({",".join(columns)}) VALUES ({",".join(values)})'
        log.info(f"_insert: execute {sql}")
        try:
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            st = traceback.extract_stack()
            raise RuntimeError(f"_insert: {e}\n{st}")

    def _select(self, table: str, fields: list[str], filter: dict) -> list[tuple]:
        cond = self._gen_cond(filter)
        fields_s = ",".join(fields) if bool(fields) else "*"
        sql = f"SELECT {fields_s} FROM {table} {cond}"
        log.info(f"_select: execute {sql}")
        try:
            result = self.cur.execute(sql)
            return [tuple(res) for res in result]
        except Exception as e:
            st = traceback.extract_stack()
            raise RuntimeError(f"_select: {e}\n{st}")

    def _update(self, table: str, fields: dict, filter: dict) -> None:
        cond = self._gen_cond(filter)
        fields_s = "SET " + ",".join([f'"{k}"="{v}"' for k, v in fields.items()])
        sql = f"UPDATE {table} {fields_s} {cond}"
        log.info(f"_update: execute {sql}")
        try:
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            st = traceback.extract_stack()
            raise RuntimeError(f"_update: {e}\n{st}")

    def _delete(self, table: str, filter: dict) -> None:
        cond = self._gen_cond(filter)
        sql = f"DELETE FROM {table} {cond}"
        log.info(f"_delete: execute {sql}")
        try:
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            st = traceback.extract_stack()
            raise RuntimeError(f"_delete: {e}\n{st}")

    def _get_id_by_word(self, word: str) -> int:
        res = self._select("words", ["id"], {"word": word})
        if len(res) == 0:
            raise KeyError(f'_get_id_by_word: no such word: "{word}"')
        else:
            return int(res[0][0])

    def insert_word(self, word: str, mastered: bool = False) -> int:
        try:
            wid = self._get_id_by_word(word)
        except KeyError:
            self._insert("words", {"word": word, "create_time": cur_utc_timestamp()})
            log.info(f'new word "{word}"')
            wid = self._get_id_by_word(word)
        self.master_word(wid, mastered)
        return wid

    def master_word(self, word: str, mastered: bool = True) -> None:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        flag = "TRUE" if mastered else "FALSE"
        res = self._select("mastered", ["id"], {"word": wid})
        if len(res) == 0:
            self._insert(
                "mastered",
                {"word": wid, "mastered": flag, "update_time": cur_utc_timestamp()},
            )
        else:
            mid = int(res[0])
            self._update(
                "mastered",
                {"mastered": flag, "update_time": cur_utc_timestamp()},
                {"id": mid},
            )
        log.info(f'mark word "{word}" as {"mastered" if mastered else "unmastered"}')

    def is_mastered(self, word: str) -> bool:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        res = self._select("mastered", ["mastered"], {"word": wid})
        assert len(res) > 0
        return res[0] == "TRUE"

    def insert_context(self, word: str, context: str) -> None:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        contexts = self._select("context", ["context"], {"word": wid})
        if context not in contexts:
            self._insert(
                "context",
                {"word": wid, "context": context, "create_time": cur_utc_timestamp()},
            )
            log.info(f'insert new context "{context}" of word "{word}"')

    def insert_define(self, word: str, category: str, define: str) -> None:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        res = self._select("define", ["word"], {"word": wid})
        if len(res) == 0:
            self._insert(
                "define",
                {
                    "word": wid,
                    "category": category,
                    "define": define,
                    "create_time": cur_utc_timestamp(),
                },
            )
            log.info(f'insert new define {category}:"{define}" of word "{word}"')

    def retrive_words(self) -> list[str]:
        return self._select("words", ["word"], None)

    def retrive_context(self, word: str) -> list[str]:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        return self._select("context", ["context"], {"word": wid})

    def retrive_define(self, word: str) -> dict[str, list[str]]:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        res = self._select("define", ["category", "define"], {"word": wid})
        result = {}
        for cat, define in res:
            result.setdefault(cat, []).append(define)
        return result

    def retrive_record(self, word: str) -> dict:
        wid = self._get_id_by_word(word)
        mastered = self.is_mastered(wid)
        contexts = self.retrive_context(wid)
        defines = self.retrive_define(wid)
        return {
            "word": word,
            "mastered": mastered,
            "context": contexts,
            "definitions": defines,
        }

    def delete_word(self, word: str) -> bool:
        wid = self._get_id_by_word(word)
        self._delete("words", {"id": wid})

    def purge(self, tables=TABLES) -> int:
        cnt = len(self._select("words", ["id"], None))
        self._delete("words", None)
        return cnt

    def migrate(self, records: list[dict], verbose=False) -> int:
        try:
            cnt = 0
            for record in records:
                word = record.get("word", None)
                mastered = record.get("mastered", False)
                if word is None:
                    continue
                wid = self.insert_word(word, mastered)
                if wid is None:
                    continue
                cnt += 1
                for context in record["context"]:
                    self.insert_context(wid, context)
                defines = record["definitions"]
                if isinstance(defines, str):
                    continue
                for cat, defines in defines.items():
                    for define in defines:
                        self.insert_define(wid, cat, define)
                if verbose:
                    print(record)
            return cnt
        except Exception as e:
            log.warning(e)
            return cnt

    def dump(self) -> list[dict]:
        try:
            return [self.retrive_record(word) for word in self.retrive_words()]
        except Exception as e:
            log.warning(e)
            return None
