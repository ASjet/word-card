package api

import (
	"log"
	"net/http"
	"strings"
)

type ApiHandler struct {
	handler func(w http.ResponseWriter, r *http.Request) error
	methods []string
}

func newHandler(handler func(w http.ResponseWriter, r *http.Request) error,
	methods ...string) *ApiHandler {
	return &ApiHandler{
		handler: handler,
		methods: methods,
	}
}

type ApiHandlerMap map[string]*ApiHandler

type RestRouter struct {
	prefix   string
	handlers ApiHandlerMap
}

func (h *RestRouter) Path(r *http.Request) string {
	return strings.TrimPrefix(r.URL.Path, h.prefix)
}

func (h *RestRouter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	log.Printf("[%s]%s %s", r.RemoteAddr, r.Method, r.URL.Path)
	handler, ok := h.handlers[h.Path(r)]
	if !ok {
		log.Printf("invalid request path: %s", r.URL.Path)
		w.WriteHeader(404)
		return
	}
	allow := false
	for _, method := range handler.methods {
		if r.Method == method {
			allow = true
			break
		}
	}
	if !allow {
		log.Printf("method not allowed: %s %s", r.Method, r.URL.Path)
		w.WriteHeader(405)
		return
	}
	err := handler.handler(w, r)
	if err != nil {
		log.Printf("internal error: %v", err)
		w.WriteHeader(500)
	}
}
