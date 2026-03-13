import requests
import xml.etree.ElementTree as ET
import pandas as pd


def get_history(currency_code="R01235", start="01/01/2020", end="08/03/2026"):
    url = f"https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start}&date_req2={end}&VAL_NM_RQ={currency_code}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_history(xml_data):
    root = ET.fromstring(xml_data)
    data = []

    for record in root.findall("Record"):
        date = record.attrib["Date"]
        value = record.findtext("Value")
        if value is not None:
            val = value.replace(",", ".")
            data.append([date, float(val)])

    return data


xml_data = get_history()

data = parse_history(xml_data)
df = pd.DataFrame(data, columns=["date", "rate"])  # type: ignore
df.to_csv("usd_history.csv", index=False)
