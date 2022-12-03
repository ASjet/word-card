package assets

import (
	"embed"
	"io/fs"
	"net/http"
)

var (
	//go:embed build/*
	content embed.FS
	MemFs   http.FileSystem
)

func init() {
	subFs, err := fs.Sub(content, "build")
	if err == nil {
		MemFs = http.FS(subFs)
	}
}
