package web

import (
	"fmt"
	"log"
	"net/http"
	"wordcard/assets"
	"wordcard/web/rest"
)

type Router struct {
	name   string
	path   string
	router http.Handler
}

var apiRouters []*Router

func Register(name, prefix string, router http.Handler) {
	apiRouters = append(apiRouters, &Router{
		name:   name,
		path:   prefix,
		router: router,
	})
}

func init() {
	apiRouters = make([]*Router, 0, 2)
	Register("page", "/", http.FileServer(assets.MemFs))
	Register("restv1", "/v1/", rest.NewRestV1("/v1/"))
}

type Server struct {
	addr string
}

func NewServer(addr string, port uint) *Server {
	return &Server{
		addr: fmt.Sprintf("%s:%d", addr, port),
	}
}

func (s *Server) Run() error {
	for _, r := range apiRouters {
		log.Printf("Start %s server on %q", r.name, r.path)
		http.Handle(r.path, r.router)
	}
	return http.ListenAndServe(s.addr, nil)
}
