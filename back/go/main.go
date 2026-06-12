package main

import (
	"fmt"
	"net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"message": "Hello, World! Welcome to Go REST API"}`)
}

func testHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"message":"test"}`)
}

func main() {
	// mux := http.NewServeMux()

	// mux.HandleFunc("GET /", helloHandler)
	// mux.HandleFunc("GET /test", testHandler)
	http.HandleFunc("/", helloHandler)
	http.HandleFunc("/test", testHandler)

	fmt.Println("Server is listening...")
	http.ListenAndServe("localhost:8080", nil)
}
