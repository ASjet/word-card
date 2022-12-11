package api

import (
	"wordcard/model"
)

type API interface {
	Query(word, lang string) error
	Parse() (*model.WordDefine, error)
}
