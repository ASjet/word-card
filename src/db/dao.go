package db

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"reflect"
	"strings"
	"time"

	_ "modernc.org/sqlite"
)

const (
	DB_DRIVER    = "sqlite"
	DB_NAME      = "./words.db"
	TAG_NAME     = "schema"
	TBL_WORDS    = "words"
	TBL_CONTEXT  = "context"
	TBL_DEFINE   = "define"
	TBL_MASTERED = "mastered"
	TIMESTAMP    = "CreateTime"
)

var (
	DBTBL_INIT_QUERYS map[string]string = map[string]string{
		"words": `CREATE TABLE words (
			id INTEGER PRIMARY KEY,
			word VARCHAR(30) UNIQUE,
			create_time INTEGER
		)`,
		"context": `CREATE TABLE context (
			id INTEGER PRIMARY KEY,
			word INTEGER,
			context VARCHAR(256),
			create_time INTEGER,
			FOREIGN KEY (word) REFERENCES words (id) ON DELETE CASCADE
		)`,
		"define": `CREATE TABLE define (
			id INTEGER PRIMARY KEY,
			word INTEGER ,
			category VARCHAR(30),
			define VARCHAR(512),
			create_time INTEGER,
			FOREIGN KEY (word) REFERENCES words (id) ON DELETE CASCADE
		)`,
		"mastered": `CREATE TABLE mastered (
			id INTEGER PRIMARY KEY,
			word INTEGER ,
			mastered INTEGER DEFAULT FALSE,
			update_time INTEGER,
			FOREIGN KEY (word) REFERENCES words (id) ON DELETE CASCADE
		)`,
	}
)

type Record struct {
	Word        string              `json:"word"`
	Contexts    []string            `json:"context,omitempty"`
	Mastered    bool                `json:"mastered,omitempty"`
	Definitions map[string][]string `json:"definitions,omitempty"`
}

type Dao struct {
	db *sql.DB
}

func NewDao() (*Dao, error) {
	_, err := os.Stat(DB_NAME)
	init := os.IsNotExist(err)

	log.Printf("connect to %s database %q", DB_DRIVER, DB_NAME)
	db, err := sql.Open(DB_DRIVER, DB_NAME)
	if err != nil {
		return nil, err
	}

	// Turn on foreign key to support ON DELETE CASCADE
	_, err = db.Exec("PRAGMA foreign_keys = ON")
	if err != nil {
		return nil, err
	}
	log.Println("PRAGMA foreign_keys = ON")

	if init {
		log.Printf("init database")
		for tbl, query := range DBTBL_INIT_QUERYS {
			_, err := db.Exec(query)
			log.Printf("create table %q", tbl)
			if err != nil {
				return nil, err
			}
		}
	}

	return &Dao{
		db: db,
	}, nil
}

// row must be a pointer
func (d *Dao) Insert(ctx context.Context, table string, row any) (int64, error) {
	var vals []any
	var fields []string

	v := reflect.ValueOf(row).Elem()
	t := v.Type()

	v.FieldByName(TIMESTAMP).SetInt(time.Now().Unix())

	for _, sf := range reflect.VisibleFields(t) {
		if field, ok := sf.Tag.Lookup(TAG_NAME); ok {
			fields = append(fields, field)
			vals = append(vals, v.FieldByName(sf.Name).Interface())
		}
	}
	query := fmt.Sprintf("INSERT INTO %s (%s) VALUES (%s)", table,
		strings.Join(fields, ","), repeatJoin("?", len(vals), ","))

	result, err := d.db.ExecContext(ctx, query, vals...)
	if err != nil {
		return -1, fmt.Errorf("err: %v\nsql: %s\nargs: %v", err, query, vals)
	}

	id, err := result.LastInsertId()
	if err != nil {
		return id, err
	}
	log.Printf("insert to %s, id = %d", table, id)
	return id, nil
}

func (d *Dao) Select(ctx context.Context, table string,
	conds map[string]any, fields ...string) (*sql.Rows, error) {
	cond, args := genPairs(" WHERE ", conds)

	fieldQuery := "*"
	if len(fields) > 0 {
		fieldQuery = strings.Join(fields, ",")
	}
	query := fmt.Sprintf("SELECT %s FROM %s%s", fieldQuery, table, cond)

	rows, err := d.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("err: %v\nsql: %s\nargs: %v", err, query, args)
	}
	log.Printf("query from %s", table)
	return rows, nil
}

func (d *Dao) Update(ctx context.Context, table string,
	fields, conds map[string]any) (int64, error) {
	val, args := genPairs(" SET ", fields)
	cond, condArgs := genPairs(" WHERE ", conds)
	args = append(args, condArgs...)

	query := fmt.Sprintf("UPDATE %s%s%s", table, val, cond)

	result, err := d.db.ExecContext(ctx, query, args...)
	if err != nil {
		return -1, fmt.Errorf("err: %v\nsql: %s\nargs: %v", err, query, args)
	}
	n, err := result.RowsAffected()
	if err != nil {
		return n, err
	}
	log.Printf("update %s, %d row(s) affected", table, n)
	return n, nil
}

func (d *Dao) Delete(ctx context.Context, table string,
	conds map[string]any) (int64, error) {
	cond, args := genPairs(" WHERE ", conds)

	query := fmt.Sprintf("DELETE FROM %s%s", table, cond)

	result, err := d.db.ExecContext(ctx, query, args...)
	if err != nil {
		return -1, fmt.Errorf("err: %v\nsql: %s\nargs: %v", err, query, args)
	}
	n, err := result.RowsAffected()
	if err != nil {
		return n, err
	}
	log.Printf("delete from %s, %d row(s) affected", table, n)
	return n, nil
}

func (d *Dao) InsertWord(ctx context.Context,
	word *Words) (int64, error) {
	return d.Insert(ctx, TBL_WORDS, word)
}

func (d *Dao) InsertContext(ctx context.Context,
	context *Context) (int64, error) {
	return d.Insert(ctx, TBL_CONTEXT, context)
}

func (d *Dao) InsertDefine(ctx context.Context,
	define *Define) (int64, error) {
	return d.Insert(ctx, TBL_DEFINE, define)
}

func (d *Dao) MasterWord(ctx context.Context,
	mastered Mastered) error {
	_, err := d.Update(ctx, TBL_MASTERED,
		map[string]any{"mastered": mastered.Mastered},
		map[string]any{"word": mastered.Word})
	if err != nil {
		_, err = d.Insert(ctx, TBL_MASTERED, mastered)
		return err
	}
	return nil
}

func (d *Dao) IsMastered(ctx context.Context, word int64) bool {
	rows, err := d.Select(ctx, TBL_MASTERED,
		map[string]any{"word": word}, "mastered")
	if err != nil {
		return false
	}
	defer rows.Close()

	mastered := false
	for rows.Next() {
		rows.Scan(&mastered)
	}
	return mastered
}

func (d *Dao) GetWords(ctx context.Context) ([]string, error) {
	rows, err := d.Select(ctx, TBL_WORDS, nil, "word")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	res := make([]string, 0)
	for rows.Next() {
		var word string
		err := rows.Scan(&word)
		if err != nil {
			return res, err
		}
		res = append(res, word)
	}
	return res, nil
}

func (d *Dao) GetWordId(ctx context.Context, word string) (int64, error) {
	rows, err := d.Select(ctx, TBL_WORDS, map[string]any{"word": word}, "id")
	if err != nil {
		return -1, err
	}
	defer rows.Close()

	var id int64 = -1
	for rows.Next() {
		err = rows.Scan(&id)
		if err != nil {
			return -1, err
		}
	}
	if id == -1 {
		return id, fmt.Errorf("no such word: %q", word)
	}
	return id, nil
}

func (d *Dao) GetContexts(ctx context.Context, word int64) ([]string, error) {
	rows, err := d.Select(ctx, TBL_CONTEXT,
		map[string]any{"word": word}, "context")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	res := make([]string, 0)
	for rows.Next() {
		var context string
		err = rows.Scan(&context)
		if err != nil {
			return res, err
		}
		res = append(res, context)
	}
	return res, nil
}

func (d *Dao) GetDefine(ctx context.Context,
	word int64) (map[string][]string, error) {
	rows, err := d.Select(ctx, TBL_DEFINE,
		map[string]any{"word": word}, "category", "define")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	res := make(map[string][]string)
	for rows.Next() {
		var category, define string
		err := rows.Scan(&category, &define)
		if err != nil {
			return res, nil
		}
		res[category] = append(res[category], define)
	}
	return res, nil
}

func (d *Dao) DelWord(ctx context.Context, id int64) error {
	_, err := d.Delete(ctx, TBL_WORDS, map[string]any{"id": id})
	return err
}

func (d *Dao) PurgeDB(ctx context.Context) (int64, error) {
	return d.Delete(ctx, TBL_WORDS, nil)
}

func (d *Dao) InsertRecord(ctx context.Context, record *Record) error {
	tx, err := d.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}

	ts := time.Now().Unix()

	result, err := tx.Exec("INSERT INTO words (word,create_time) VALUES (?,?)",
		record.Word, ts)
	if err != nil {
		return err
	}
	wid, err := result.LastInsertId()
	if err != nil {
		return err
	}

	_, err = tx.Exec("INSERT INTO mastered (word,mastered,update_time) VALUES (?,?,?)",
		wid, false, ts)
	if err != nil {
		return err
	}

	for _, context := range record.Contexts {
		_, err := tx.Exec("INSERT INTO context (word,context,create_time) VALUES (?,?,?)",
			wid, context, ts)
		if err != nil {
			return err
		}
	}

	for category, defines := range record.Definitions {
		for _, define := range defines {
			_, err := tx.Exec("INSERT INTO define (word,category,define,create_time) VALUES (?,?,?,?)",
				wid, category, define, ts)
			if err != nil {
				return err
			}
		}
	}

	return tx.Commit()
}

func repeatJoin(str string, cnt int, sep string) string {
	strs := make([]string, 0, cnt)
	for i := 0; i < cnt; i++ {
		strs = append(strs, str)
	}
	return strings.Join(strs, sep)
}

func genPairs(preload string, pairs map[string]any) (query string, args []any) {
	if len(pairs) > 0 {
		query = preload
		fields := make([]string, 0, len(pairs))
		args = make([]any, 0, len(pairs))
		for f, v := range pairs {
			fields = append(fields, f+" = ?")
			args = append(args, v)
		}
		query += strings.Join(fields, ",")
	}
	return
}
