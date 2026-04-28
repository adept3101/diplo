package models

import (
	"time"
)

type Users struct {
	ID       int       `json:"id"`
	Login    string    `json:"login"`
	Password string    `json:"password"`
	DateReg  time.Time `json:"DateReg"`
}
