package db

import (
	"fmt"
	"context"
	"os"
	"github.com/jackc/pgx/v5"
)

func Conn(){
	url := "postgres://postgres:3101@localhost:5432/diplom"
    conn, err := pgx.Connect(context.Background(), url)
    if err != nil {
        fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
        os.Exit(1)
    }
    defer conn.Close(context.Background())

    fmt.Println("Успешное подключение!")
}
