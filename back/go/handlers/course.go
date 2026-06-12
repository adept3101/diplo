package handlers

import (
	"fmt"
	"net/http"
	"io"
	"encoding/xml"
	"encoding/json"
	"bytes"
	
)

type ValCurs struct {
	XMLName xml.Name `xml:"ValCurs"`
	Date    string   `xml:"Date,attr"`
	Valute  []Valute `xml:"Valute"`
}

type Valute struct {
	ID       string `xml:"ID,attr"`
	CharCode string `xml:"CharCode"`
	Nominal  int    `xml:"Nominal"`
	Name     string `xml:"Name"`
	Value    string `xml:"Value"`
}

func get_cb() ([]byte, error) {
	client := &http.Client{}

	url := "https://www.cbr.ru/scripts/XML_daily.asp"

	req, err := http.NewRequest("GET", url, nil)

	if err != nil {
		fmt.Println("Ошибка создания запроса:", err)
	}

	req.Header.Set("User-Agent", "Mozilla/5.0")
	resp, err := client.Do(req)

	if err != nil {
		fmt.Println("Ошибка запроса:", err)
	}

	defer resp.Body.Close()

	return io.ReadAll(resp.Body)
}

func xmlToJSON(xmlData []byte) (string, error) {
	var data ValCurs

	decoder := xml.NewDecoder(bytes.NewReader(xmlData))
	decoder.CharsetReader = charset.NewReaderLabel

	if err := decoder.Decode(&data); err != nil {
		return "", err
	}

	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return "", err
	}

	return string(jsonData), nil
}
