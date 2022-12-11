package model

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

type Words struct {
	Word       string `schema:"word"`
	CreateTime int64  `schema:"create_time"` // Ignore
}

type Context struct {
	Word       int64  `schema:"word"`
	Context    string `schema:"context"`
	CreateTime int64  `schema:"create_time"` // Ignore
}

type Define struct {
	Word       int64  `schema:"word"`
	Category   string `schema:"category"`
	Define     string `schema:"define"`
	CreateTime int64  `schema:"create_time"` // Ignore
}

type Mastered struct {
	Word       int64 `schema:"word"`
	Mastered   bool  `schema:"mastered"`
	CreateTime int64 `schema:"create_time"` // Ignore
}

type WordDefine struct {
	Word     string              `json:"word"`
	Phonetic string              `json:"phonetic"`
	Defines  map[string][]string `json:"defines"`
	s        string
}

func (d *WordDefine) String() string {
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
