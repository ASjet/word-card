import logging
import sqlite3
from pathlib import Path
from datetime import datetime

WORD_DB = "words.db"
TABLES = ["words", "context", "define"]
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

    def __del__(self):
        self.con.commit()
        self.con.close()

    def init_db(self):
        try:
            self.con = sqlite3.connect(self.DB_NAME)
            self.cur = self.con.cursor()
            sql = """
            CREATE TABLE words (
                id INTEGER PRIMARY KEY,
                word VARCHAR(30) UNIQUE,
                mastered INTEGER DEFAULT FALSE,
                create_time INTEGER
            ) """
            self.cur.execute(sql)
            sql = """
            CREATE TABLE context (
                id INTEGER PRIMARY KEY,
                word INTEGER,
                context VARCHAR(256),
                create_time INTEGER,
                FOREIGN KEY (word) REFERENCES words ON DELETE CASCADE
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
                FOREIGN KEY (word) REFERENCES words ON DELETE CASCADE
            )
            """
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            log.warning(e, sql)

    def _get_id_by_word(self, word: str) -> int:
        res = self.cur.execute(f'SELECT id FROM words WHERE word = "{word}"').fetchone()
        if len(res) == 0:
            return None
        else:
            return int(res[0])

    def _insert_sql(self, table: str, fields: dict) -> str:
        columns = []
        values = []
        for k, v in fields.items():
            columns.append(k)
            values.append(f'"{v}"')
        sql = f'INSERT INTO {table} ({",".join(columns)}) VALUES ({",".join(values)})'
        return sql

    def _select_sql(self, table: str, _fields: list[str], _cond: dict) -> str:
        if bool(_cond):
            cond = "WHERE " + ",".join([f'"{k}"="{v}"' for k, v in _cond.items()])
        else:
            cond = ""
        fields = ",".join(_fields) if bool(_fields) else "*"
        sql = f"SELECT {fields} FROM {table} {cond}"
        return sql

    def insert_word(self, word: str) -> bool:
        ts = cur_utc_timestamp()
        try:
            sql = self._insert_sql("words", {"word": word, "create_time": ts})
            self.cur.execute(sql)
            self.con.commit()
            log.info(f'Insert new word "{word}"')
            return True
        except Exception as e:
            log.warning(f"insert_word: {e}\nSQL: {sql}")
            return False

    def insert_context(self, word: str, context: str) -> bool:
        ts = cur_utc_timestamp()
        try:
            wid = word if isinstance(word, int) else self._get_id_by_word(word)
            if wid is None:
                return False
            sql = self._insert_sql(
                "context", {"word": wid, "context": context, "create_time": ts}
            )
            self.cur.execute(sql)
            self.con.commit()
            log.info(f'Insert new context "{context}" of word "{word}"')
            return True
        except Exception as e:
            log.warning(f"insert_context: {e}\nSQL: {sql}")
            return False

    def insert_define(self, word: str, category: str, define: str) -> bool:
        ts = cur_utc_timestamp()
        try:
            wid = word if isinstance(word, int) else self._get_id_by_word(word)
            if wid is None:
                return False
            sql = self._insert_sql(
                "define",
                {
                    "word": wid,
                    "category": category,
                    "define": define,
                    "create_time": ts,
                },
            )
            self.cur.execute(sql)
            self.con.commit()
            log.info(f'Insert new define {category}:"{define}" of word "{word}"')
            return True
        except Exception as e:
            log.warning(f"insert_define: {e}\nSQL: {sql}")
            return False

    def insert_record(self, word: str, context: str) -> bool:
        self.insert_word(word)
        return self.insert_context(word, context)

    def retrive_words(self) -> list[str]:
        try:
            sql = self._select_sql("words", ["word"], None)
            return [res[0] for res in self.cur.execute(sql)]
        except Exception as e:
            log.warning(f"retrive_words: {e}\nSQL: {sql}")
            return None

    def retrive_context(self, word: str) -> list[str]:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        if wid is None:
            return []

        try:
            sql = self._select_sql("context", ["context"], {"word": wid})
            return [res[0] for res in self.cur.execute(sql)]
        except Exception as e:
            log.warning(f"retrive_context: {e}\nSQL: {sql}")
            return None

    def retrive_define(self, word: str) -> dict[str, list[str]]:
        wid = word if isinstance(word, int) else self._get_id_by_word(word)
        if wid is None:
            return []

        try:
            sql = self._select_sql("define", ["category", "define"], {"word": wid})
            res = self.cur.execute(sql)
            result = {}
            for cat, define in res:
                result.setdefault(cat, []).append(define)
            return result
        except Exception as e:
            log.warning(f"retrive_define: {e}\nSQL: {sql}")
            return None

    def purge(self, tables=TABLES) -> int:
        try:
            cnt = 0
            for table in tables:
                sql = f"DELETE FROM {table}"
                self.cur.execute(sql)
                cnt += 1
            self.con.commit()
            return cnt
        except Exception as e:
            log.warning(f"purge: {e}\nSQL: {sql}")
            return cnt

    def migrate(self, records: list[dict], verbose=False) -> int:
        try:
            cnt = 0
            for record in records:
                word = record.get("word", None)
                if word is None:
                    continue
                if self.insert_word(word):
                    cnt += 1
                wid = self._get_id_by_word(word)
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
            self.con.commit()
            return cnt
        except Exception as e:
            log.warning(f"migrate: {e}\nrecord: {record}")
            return cnt

    def dump(self) -> list[dict]:
        try:
            res = []
            for word in self.retrive_words():
                wid = self._get_id_by_word(word)
                contexts = self.retrive_context(wid)
                defines = self.retrive_define(wid)
                res.append({"word": word, "context": contexts, "definitions": defines})
            return res
        except Exception as e:
            log.warning(f"dump: {e}")
            return None
