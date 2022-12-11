package api

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFreeDict(t *testing.T) {
	word := "word"
	api := NewFreeDict()
	err := api.Query(word, "en")
	assert.NoError(t, err)

	define, err := api.Parse()
	assert.NoError(t, err)

	assert.Len(t, define.String(), 1430)
}
