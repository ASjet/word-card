package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

const (
	FD_BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries"
)

type Definition struct {
	Definition string `json:"definition"`
}

type Meaning struct {
	Category    string       `json:"partOfSpeech"`
	Definitions []Definition `json:"definitions"`
}

type FDResult struct {
	Word     string    `json:"word"`
	Phonetic string    `json:"phonetic"`
	Meanings []Meaning `json:"meanings"`
}

type FreeDict struct {
	Results []FDResult
	Define  *Define
}

func NewFreeDict() API {
	return new(FreeDict)
}

func (fd *FreeDict) Query(word, lang string) error {
	resp, err := http.Get(fmt.Sprintf("%s/%s/%s", FD_BASE_URL,
		lang, strings.ToLower(word)))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	decoder := json.NewDecoder(resp.Body)
	return decoder.Decode(&fd.Results)
}

func (fd *FreeDict) Parse() (*Define, error) {
	if fd.Define == nil {
		if len(fd.Results) == 0 {
			return nil, fmt.Errorf("no result found, query first")
		}
		fd.Define = new(Define)
		fd.Define.Word = fd.Results[0].Word
		fd.Define.Phonetic = fd.Results[0].Phonetic

		defines := make(map[string][]string)
		for _, res := range fd.Results {
			for _, means := range res.Meanings {
				category := means.Category
				for _, define := range means.Definitions {
					defines[category] = append(defines[category], define.Definition)
				}
			}
		}
		fd.Define.Defines = defines
	}
	return fd.Define, nil
}
