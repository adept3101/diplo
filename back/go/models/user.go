package models

import (
	"time"
	"gorm.io/gorm"
	"gorm.io/driver/postgres"
)

// type User struct {
// 	ID int `json:"id"`
// 	Login string `json:"login"`
// 	Password string `json:"password"`
// 	DateReg time.Time `json:"date_reg"`
// }

type User struct {
	gorm.Model
	ID int `gorm:"primaryKey"`
	Login string 
	Password string 
	DateReg time.Time 
}

func Conn() {
//     dsn := "host=localhost user=user dbname=db password=password sslmode=disable"
//     db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
dsn := "host=localhost user=postgres password=3101 dbname=diplom port=5432 sslmode=disable"

  db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
  if err != nil {
    panic("failed to connect database")
  }

  _ = db
}
