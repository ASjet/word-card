package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"wordcard/db"
	"wordcard/web"
)

var (
	port  uint
	purge bool
	dump  bool
)

func init() {
	flag.UintVar(&port, "p", 8000, "Port")
	flag.BoolVar(&purge, "c", false, "Clear database")
	flag.BoolVar(&dump, "d", false, "Dump database to readable records")
}

func main() {
	if purge {
		dao, err := db.NewDao()
		if err != nil {
			log.Fatal(err)
		}
		n, err := dao.PurgeDB(context.TODO())
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%d record(s) deleted", n)
		return
	}
	log.Printf("Listen on port %d", port)
	srv := web.NewServer("localhost", port)
	log.Fatal(srv.Run())
}
