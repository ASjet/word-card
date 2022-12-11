package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"wordcard/model"
)

const (
	OD_BASE_URL = "https://od-api.oxforddictionaries.com/api/v2/entries"
)

var (
	API_ID  string
	API_KEY string
)

func init() {
	API_ID = os.Getenv("API_ID")
	API_KEY = os.Getenv("API_KEY")
}

type Sense struct {
	Definitions []string `json:"definitions"`
}

type Entry struct {
	Senses []Sense `json:"senses"`
}

type Category struct {
	Category string `json:"text"`
}

type LexicalEntry struct {
	Entries  []Entry  `json:"entries"`
	Category Category `json:"lexicalCategory"`
}

type Result struct {
	Entries []LexicalEntry `json:"lexicalEntries"`
}

type ODResult struct {
	Word    string   `json:"word"`
	Results []Result `json:"results"`
}

type OxfordDict struct {
	Result *ODResult
	Define *model.WordDefine
}

func NewOxfordDict() API {
	return new(OxfordDict)
}

func (od *OxfordDict) Query(word, lang string) error {
	client := new(http.Client)
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/%s/%s?fields=definitions",
		OD_BASE_URL, lang, strings.ToLower(word)), nil)
	if err != nil {
		return err
	}
	req.Header.Add("accept", "application/json")
	req.Header.Add("app_id", API_ID)
	req.Header.Add("app_key", API_KEY)

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	decoder := json.NewDecoder(resp.Body)
	od.Result = new(ODResult)
	return decoder.Decode(od.Result)
}

func (od *OxfordDict) Parse() (*model.WordDefine, error) {
	if od.Define == nil {
		if od.Result == nil {
			return nil, fmt.Errorf("no result found, query first")
		}
		od.Define = new(model.WordDefine)
		od.Define.Word = od.Result.Word

		defines := make(map[string][]string)
		for _, res := range od.Result.Results {
			for _, lentries := range res.Entries {
				category := lentries.Category.Category
				for _, entry := range lentries.Entries {
					for _, sense := range entry.Senses {
						defines[category] = append(defines[category], sense.Definitions...)
					}
				}
			}
		}
		od.Define.Defines = defines
	}
	return od.Define, nil
}
