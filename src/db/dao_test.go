package db

import (
	"context"
	"os"
	"testing"
	"wordcard/model"

	"github.com/stretchr/testify/assert"
)

type DaoTester struct {
	t   *testing.T
	dao *Dao
}

func newDaoTester(t *testing.T) *DaoTester {
	os.Remove(DB_NAME)
	dao, err := NewDao()
	assert.NoError(t, err)
	return &DaoTester{
		t:   t,
		dao: dao,
	}
}

func (t *DaoTester) insertWords(words ...string) []int64 {
	ids := make([]int64, 0, len(words))
	for _, word := range words {
		id, err := t.dao.Insert(context.TODO(), TBL_WORDS, &model.Words{Word: word})
		assert.NoError(t.t, err)
		ids = append(ids, id)
	}
	assert.Len(t.t, ids, len(words))
	return ids
}

func (t *DaoTester) getWords() []string {
	words, err := t.dao.GetWords(context.TODO())
	assert.NoError(t.t, err)
	return words
}

func TestRepeatJoin(t *testing.T) {
	wanted := "?,?,?"
	actually := repeatJoin("?", 3, ",")
	if wanted != actually {
		t.Fatalf("wanted\n%s\nactually\n%s", wanted, actually)
	}
}

func TestGenPair(t *testing.T) {
	wantedQuery := " WHERE word = ?,id = ?"
	wantedArgs := []any{"test", 1}
	actuallyQuery, actuallyArgs := genPairs(" WHERE ", map[string]any{
		"word": wantedArgs[0],
		"id":   wantedArgs[1],
	})
	assert.Equal(t, wantedQuery, actuallyQuery)
	assert.Equal(t, wantedArgs, actuallyArgs)
}

func TestInsert(t *testing.T) {
	rawWords := []string{"test", "insert", "hello", "word"}

	dt := newDaoTester(t)

	dt.insertWords(rawWords...)
	echoWords := dt.getWords()

	assert.ElementsMatch(t, rawWords, echoWords)
}

func TestPurge(t *testing.T) {
	rawWords := []string{"test", "purge"}
	dt := newDaoTester(t)

	dt.insertWords(rawWords...)
	assert.ElementsMatch(t, rawWords, dt.getWords())

	n, err := dt.dao.PurgeDB(context.TODO())
	assert.NoError(t, err)
	assert.Len(t, rawWords, int(n))
	assert.Len(t, dt.getWords(), 0)
}
