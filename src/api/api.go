package api

import (
	"bytes"
	"log"
	"text/template"
)

const DEFINE_TEMPLATE = `{{.Word}} {{.Phonetic}}

{{range $cate, $defines := .Defines}}{{$cate}}
{{range $i, $define := $defines}}    {{$i}}. {{$define}}
{{end}}{{end}}`

var tmpl = template.Must(template.New("define").Parse(DEFINE_TEMPLATE))

type API interface {
	Query(word, lang string) error
	Parse() (*Define, error)
}

type Define struct {
	Word     string
	Phonetic string
	Defines  map[string][]string
	s        string
}

func (d *Define) String() string {
	if d.s == "" {
		buf := new(bytes.Buffer)
		err := tmpl.Execute(buf, d)
		if err != nil {
			log.Print(err)
		}
		d.s = buf.String()
	}
	return d.s
}
