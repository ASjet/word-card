package api

import (
	"encoding/json"
	"log"
	"net/http"
	"wordcard/db"
)

var dao *db.Dao

func init() {
	var err error
	dao, err = db.NewDao()
	if err != nil {
		log.Fatal(err)
	}
}

type Record struct {
	Word        string              `json:"word"`
	Contexts    []string            `json:"context,omitempty"`
	Mastered    bool                `json:"mastered,omitempty"`
	Definitions map[string][]string `json:"definitions,omitempty"`
}

type JsonResponse struct {
	Msg  string      `json:"msg"`
	Data interface{} `json:"data"`
}

func jsonWrapper(w http.ResponseWriter, msg string, data interface{}) {
	rsp, err := json.Marshal(&JsonResponse{Msg: msg, Data: data})
	if err != nil {
		log.Printf("internal error: %v", err)
		w.WriteHeader(500)
	}
	w.Write(rsp)
}

func NewRestV1(prefix string) *RestRouter {
	return &RestRouter{
		prefix: prefix,
		handlers: ApiHandlerMap{
			"word":   newHandler(v1Word, "GET", "POST", "DELETE"),
			"define": newHandler(v1Define, "GET"),
			"master": newHandler(v1Master, "PUT"),
		},
	}
}

func v1Word(w http.ResponseWriter, r *http.Request) error {
	switch r.Method {
	case "GET":
		words, err := dao.GetWords(r.Context())
		if err != nil {
			return err
		}
		jsonWrapper(w, "", words)
	}
	return nil
}

func v1Define(w http.ResponseWriter, r *http.Request) error {
	word := r.FormValue("word")
	wid, err := dao.GetWordId(r.Context(), word)
	if err != nil {
		return err
	}
	contexts, err := dao.GetContexts(r.Context(), wid)
	if err != nil {
		return err
	}
	defines, err := dao.GetDefine(r.Context(), wid)
	if err != nil {
		return err
	}
	mastered := dao.IsMastered(r.Context(), wid)
	record := &Record{
		Word:        word,
		Contexts:    contexts,
		Mastered:    mastered,
		Definitions: defines,
	}
	jsonWrapper(w, "", record)
	return nil
}

func v1Master(w http.ResponseWriter, r *http.Request) error {
	word := r.FormValue("word")
	wid, err := dao.GetWordId(r.Context(), word)
	if err != nil {
		return err
	}
	return dao.MasterWord(r.Context(), db.Mastered{
		Word:     wid,
		Mastered: true,
	})
}
