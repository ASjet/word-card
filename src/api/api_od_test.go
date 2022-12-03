package api

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestOnlineDict(t *testing.T) {
	word := "word"
	api := NewOnlineDict()
	err := api.Query(word, "en")
	assert.NoError(t, err)

	define, err := api.Parse()
	assert.NoError(t, err)

	assert.Len(t, define.String(), 1430)
}
