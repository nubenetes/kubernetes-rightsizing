package main

import (
	"fmt"
	"log"
	"net/http"
	"runtime"

	// Automatically adjusts GOMAXPROCS to match Linux cgroups CPU quota
	_ "go.uber.org/automaxprocs"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	response := fmt.Sprintf(
		"Status: OK\nGOMAXPROCS: %d\nAlloc: %d MiB\nSys: %d MiB\nNumGC: %d\n",
		runtime.GOMAXPROCS(0),
		m.Alloc/1024/1024,
		m.Sys/1024/1024,
		m.NumGC,
	)
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(response))
}

func main() {
	http.HandleFunc("/healthz", healthHandler)
	log.Printf("Starting Go microservice on :8080 (GOMAXPROCS: %d)", runtime.GOMAXPROCS(0))
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
