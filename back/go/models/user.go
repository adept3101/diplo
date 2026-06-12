package models

import (
	"time"
)

type Users struct {
	ID       int       `json:"id"`
	login    string    `json:"login"`
	password string    `json:"password"`
	date_reg time.Time `json:"date_reg"`
}

