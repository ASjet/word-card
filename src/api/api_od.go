package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

const (
	BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries"
)

type Definition struct {
	Definition string `json:"definition"`
}

type Meaning struct {
	Category    string       `json:"partOfSpeech"`
	Definitions []Definition `json:"definitions"`
}

type Result struct {
	Word     string    `json:"word"`
	Phonetic string    `json:"phonetic"`
	Meanings []Meaning `json:"meanings"`
}

type OnlineDict struct {
	Results []Result
	Define  *Define
}

func NewOnlineDict() API {
	return new(OnlineDict)
}

func (od *OnlineDict) Query(word, lang string) error {
	resp, err := http.Get(fmt.Sprintf("%s/%s/%s", BASE_URL,
		lang, strings.ToLower(word)))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	decoder := json.NewDecoder(resp.Body)
	return decoder.Decode(&od.Results)
}

func (od *OnlineDict) Parse() (*Define, error) {
	if od.Define == nil {
		if len(od.Results) == 0 {
			return nil, fmt.Errorf("no result found, query first")
		}
		od.Define = new(Define)
		od.Define.Word = od.Results[0].Word
		od.Define.Phonetic = od.Results[0].Phonetic

		defines := make(map[string][]string)
		for _, res := range od.Results {
			for _, means := range res.Meanings {
				category := means.Category
				for _, define := range means.Definitions {
					defines[category] = append(defines[category], define.Definition)
				}
			}
		}
		od.Define.Defines = defines
	}
	return od.Define, nil
}
