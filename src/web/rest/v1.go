package rest

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"wordcard/api"
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

type JsonResponse struct {
	Msg  string      `json:"msg"`
	Data interface{} `json:"data"`
}

func jsonWrapper(w http.ResponseWriter, code int, msg string, data interface{}) error {
	rsp, err := json.Marshal(&JsonResponse{Msg: msg, Data: data})
	if err != nil {
		return fmt.Errorf("json wrapper: %v", err)
	}
	w.WriteHeader(code)
	w.Write(rsp)
	return nil
}

func internalError(w http.ResponseWriter) error {
	return jsonWrapper(w, 500, "Internal Error", nil)
}

func invalidParameters(w http.ResponseWriter) error {
	return jsonWrapper(w, 400, "Invalid Parameters", nil)
}

func notFount(w http.ResponseWriter) error {
	return jsonWrapper(w, 404, "No such word", nil)
}

func ok(w http.ResponseWriter, msg string, data any) error {
	return jsonWrapper(w, 200, msg, data)
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
			log.Print(err)
			return internalError(w)
		}
		return ok(w, "", words)
	case "POST":
		defer r.Body.Close()
		decoder := json.NewDecoder(r.Body)
		record := new(db.Record)
		err := decoder.Decode(record)
		if err != nil {
			log.Print(err)
			return invalidParameters(w)
		}

		wid, err := dao.GetWordId(r.Context(), record.Word)
		if err != nil {
			dict := api.NewOnlineDict()
			err = dict.Query(record.Word, "en")
			if err != nil {
				log.Print(err)
				return internalError(w)
			}
			define, err := dict.Parse()
			if err != nil {
				log.Print(err)
				return internalError(w)
			}
			record.Definitions = define.Defines
			err = dao.InsertRecord(r.Context(), record)
			if err != nil {
				log.Print(err)
				return internalError(w)
			}
			return ok(w, "Record Successfully", nil)
		}
		_, err = dao.InsertContext(r.Context(), &db.Context{
			Word:    wid,
			Context: record.Contexts[0],
		})
		if err != nil {
			log.Print(err)
			return internalError(w)
		}
		return ok(w, "Record Successfully", nil)
	case "DELETE":
		word := r.FormValue("word")
		if word == "" {
			return invalidParameters(w)
		}
		wid, err := dao.GetWordId(r.Context(), word)
		if err != nil {
			return notFount(w)
		}
		err = dao.DelWord(r.Context(), wid)
		if err != nil {
			return internalError(w)
		}
		return ok(w, "Delete Successfully", nil)
	}
	return nil
}

func v1Define(w http.ResponseWriter, r *http.Request) error {
	word := r.FormValue("word")
	if word == "" {
		return invalidParameters(w)
	}
	wid, err := dao.GetWordId(r.Context(), word)
	if err != nil {
		return notFount(w)
	}
	contexts, err := dao.GetContexts(r.Context(), wid)
	if err != nil {
		log.Print(err)
		return internalError(w)
	}
	defines, err := dao.GetDefine(r.Context(), wid)
	if err != nil {
		log.Print(err)
		return internalError(w)
	}
	mastered := dao.IsMastered(r.Context(), wid)
	record := &db.Record{
		Word:        word,
		Contexts:    contexts,
		Mastered:    mastered,
		Definitions: defines,
	}
	return ok(w, "", record)
}

func v1Master(w http.ResponseWriter, r *http.Request) error {
	word := r.FormValue("word")
	if word == "" {
		return invalidParameters(w)
	}
	wid, err := dao.GetWordId(r.Context(), word)
	if err != nil {
		return notFount(w)
	}
	err = dao.MasterWord(r.Context(), db.Mastered{
		Word:     wid,
		Mastered: true,
	})
	if err != nil {
		return internalError(w)
	}
	return ok(w, "", nil)
}
