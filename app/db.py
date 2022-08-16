import logging
import sqlite3
from pathlib import Path
from datetime import datetime

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
            sql = """
            CREATE TABLE mastered (
                id INTEGER PRIMARY KEY,
                word INTEGER ,
                mastered INTEGER DEFAULT FALSE,
                update_time INTEGER,
                FOREIGN KEY (word) REFERENCES words ON DELETE CASCADE
            )
            """
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            log.warning(e, sql)

    def _parse_cond(self, cond: dict) -> str:
        if bool(cond):
            return "WHERE " + ",".join([f'"{k}"="{v}"' for k, v in cond.items()])
        else:
            return ""

    def _insert_sql(self, table: str, fields: dict) -> str:
        columns = []
        values = []
        for k, v in fields.items():
            columns.append(k)
            values.append(f'"{v}"')
        sql = f'INSERT INTO {table} ({",".join(columns)}) VALUES ({",".join(values)})'
        return sql

    def _select_sql(self, table: str, _fields: list[str], _cond: dict) -> str:
        cond = self._parse_cond(_cond)
        fields = ",".join(_fields) if bool(_fields) else "*"
        sql = f"SELECT {fields} FROM {table} {cond}"
        return sql

    def _update_sql(self, table: str, _fields: dict, _cond: dict) -> str:
        cond = self._parse_cond(_cond)
        fields = "SET " + ",".join([f'"{k}"="{v}"' for k, v in _fields.items()])
        sql = f"UPDATE {table} {fields} {cond}"
        return sql

    def _get_id_by_word(self, word: str) -> int:
        sql = self._select_sql("words", ["id"], {"word": word})
        res = self.cur.execute(sql).fetchone()
        if res is None or len(res) == 0:
            return None
        else:
            return int(res[0])

    def insert_word(self, word: str, mastered: bool = False) -> int:
        ts = cur_utc_timestamp()
        try:
            wid = self._get_id_by_word(word)
            if wid is None:
                sql = self._insert_sql("words", {"word": word, "create_time": ts})
                self.cur.execute(sql)
                self.con.commit()
                log.info(f'Insert new word "{word}"')
                wid = self._get_id_by_word(word)
            self.master_word(wid, mastered)
            return wid
        except Exception as e:
            log.warning(f"insert_word: {e}\nSQL: {sql}")
            return None

    def master_word(self, word: str, mastered: bool = True) -> bool:
        ts = cur_utc_timestamp()
        try:
            wid = word if isinstance(word, int) else self._get_id_by_word(word)
            if wid is None:
                return False
            flag = "TRUE" if mastered else "FALSE"
            sql = self._select_sql("mastered", ["id"], {"word": wid})
            res = self.cur.execute(sql).fetchone()
            if res is None or len(res) == 0:
                sql = self._insert_sql(
                    "mastered", {"word": wid, "mastered": flag, "update_time": ts}
                )
            else:
                mid = int(res[0])
                sql = self._update_sql(
                    "mastered", {"mastered": flag, "update_time": ts}, {"id": mid}
                )
            self.cur.execute(sql)
            self.con.commit()
            log.info(
                f'Update word "{word}" to {"mastered" if mastered else "unmastered"}'
            )
            return True
        except Exception as e:
            log.warning(f"master_word: {e}\nSQL: {sql}")

    def is_mastered(self, word: str) -> bool:
        try:
            wid = word if isinstance(word, int) else self._get_id_by_word(word)
            if wid is None:
                return False
            sql = self._select_sql("mastered", ["mastered"], {"word": wid})
            res = self.cur.execute(sql).fetchone()
            if res is None or len(res) == 0:
                return False
            return res[0] == "TRUE"
        except Exception as e:
            log.warning(f"is_mastered: {e}\nSQL: {sql}")
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
        wid = self.insert_word(word)
        if wid is not None:
            return self.insert_context(wid, context)
        else:
            return False

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
        try:
            sql = f'DELETE FROM words WHERE word = "{word}"'
            self.cur.execute(sql)
            self.con.commit()
            return True
        except Exception as e:
            log.warning(f"delete_word: {e}\nSQL: {sql}")
            return False

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
            self.con.commit()
            return cnt
        except Exception as e:
            log.warning(f"migrate: {e}\nrecord: {record}")
            return cnt

    def dump(self) -> list[dict]:
        try:
            return [self.retrive_record(word) for word in self.retrive_words()]
        except Exception as e:
            log.warning(f"dump: {e}")
            return None
