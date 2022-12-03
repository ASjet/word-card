package db

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
