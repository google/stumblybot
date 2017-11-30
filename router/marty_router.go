package main

/*
Copyright 2017 Google Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

		https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

import (
	"bufio"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"strconv"
	"time"
)

var (
	apiAIPort = flag.Int("apiai_port", 80, "API.AI port to listen")
	martyPort = flag.Int("marty_port", 1109, "Marty port to listen")

	mgrCh = make(chan interface{}, 1024)
)

type subscribe struct {
	conn net.Conn
}

type unsubscribe struct {
	conn net.Conn
}

type send struct {
	values   map[string]interface{}
	response map[string]interface{}
	errCh    chan error
}

type respond struct {
	values map[string]interface{}
}

type abort struct {
	id string
}

func manager() {
	conns := make(map[net.Conn]struct{})
	queries := make(map[string]*send)
	lastID := 0
	for cmd := range mgrCh {
		switch cmd := cmd.(type) {
		case subscribe:
			conns[cmd.conn] = struct{}{}
		case unsubscribe:
			delete(conns, cmd.conn)
		case *respond:
			id, ok := cmd.values["id"].(string)
			if !ok {
				log.Printf("Invalid response: id missing or not a string")
				break
			}
			query := queries[id]
			if query == nil {
				log.Printf("Response to query %d came too late", id)
				break
			}
			log.Printf("Query %s fulfilled", id)
			query.response = cmd.values
			delete(cmd.values, "id")
			query.errCh <- nil
			delete(queries, id)
		case *abort:
			query := queries[cmd.id]
			if query == nil {
				break
			}
			log.Printf("Query %s timed out", cmd.id)
			query.errCh <- errors.New("timeout")
			delete(queries, cmd.id)
		case *send:
			lastID++
			id := strconv.Itoa(lastID)
			cmd.values["id"] = id
			data, err := json.Marshal(cmd.values)
			if err != nil {
				cmd.errCh <- err
				return
			}
			log.Printf("Incoming query %s: %s", id, string(data))
			data = append(data, '\n')
			success := false
			for conn := range conns {
				conn.SetWriteDeadline(time.Now().Add(time.Second))
				if _, err := conn.Write(data); err != nil {
					log.Printf("%v: %v", conn.RemoteAddr(), err)
				} else {
					log.Printf("%v: message delivered", conn.RemoteAddr())
					success = true
				}
			}
			if !success {
				log.Printf("Incoming message dropped")
				cmd.errCh <- errors.New("message not delivered")
			} else {
				queries[id] = cmd
				// Set watchdog timer.
				go func(id string) {
					time.Sleep(5 * time.Second)
					mgrCh <- &abort{id}
				}(id)
			}
		}
	}
}

func handleMartySocket(ln net.Listener) {
	for {
		conn, err := ln.Accept()
		if err != nil {
			log.Fatal(err)
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	mgrCh <- subscribe{conn}
	defer func() {
		log.Printf("%v: connection terminated", conn.RemoteAddr())
		mgrCh <- unsubscribe{conn}
	}()
	log.Printf("%v: connection established", conn.RemoteAddr())
	rd := bufio.NewReader(conn)
	for {
		data, err := rd.ReadBytes('\n')
		if err != nil {
			if err != io.EOF {
				log.Printf("%v: %v", conn.RemoteAddr(), err)
			}
			return
		}
		log.Printf("%v: responded with %s", conn.RemoteAddr(), string(data))
		var values map[string]interface{}
		if err := json.Unmarshal(data, &values); err != nil {
			log.Printf("%v: %v", conn.RemoteAddr(), err)
			return
		}
		mgrCh <- &respond{values}
	}
}

func main() {
	http.HandleFunc("/send", func(w http.ResponseWriter, r *http.Request) {
		data, err := ioutil.ReadAll(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			log.Printf("Error reading data from client: %v", err)
			fmt.Fprint(w, "Error reading data\n")
			return
		}
		var values map[string]interface{}
		if err := json.Unmarshal(data, &values); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			log.Printf("Error unmarshalling JSON data from client: %v", err)
			fmt.Fprint(w, "Error processing data\n")
			return
		}
		errCh := make(chan error)
		query := &send{values, nil, errCh}
		mgrCh <- query
		if err := <-errCh; err != nil {
			if err.Error() == "timeout" {
				w.WriteHeader(http.StatusGatewayTimeout)
				fmt.Fprint(w, "Gateway Timeout\n")
			} else {
				w.WriteHeader(http.StatusBadGateway)
				fmt.Fprint(w, "Bad Gateway\n")
			}
			return
		}
		data, err = json.Marshal(query.response)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Fprint(w, "Internal Server Error\n")
			log.Printf("Error marshalling JSON: %v", err)
			return
		}
		w.Header().Add("Content-type", "application/json")
		w.Write(data)
		log.Printf("Outgoing response: %s", string(data))
	})

	ln, err := net.Listen("tcp", fmt.Sprintf(":%d", *martyPort))
	if err != nil {
		log.Fatal(err)
	}
	go handleMartySocket(ln)
	go manager()

	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", *apiAIPort), http.DefaultServeMux))
}
