from fastapi import FastAPI, APIRouter
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import joblib
from typing import List

# app = FastAPI()

router = APIRouter(prefix="/course", tags=["Course"])


# @app.get("/get_cur_cour")
async def get_cb(date_req=None):
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_req}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def parse_xml(xml_data):
    root = ET.fromstring(xml_data)

    rates = []

    for valute in root.findall("Valute"):
        char_code = valute.findtext("CharCode")
        name = valute.findtext("Name")
        nominal = valute.findtext("Nominal")
        value = valute.findtext("Value")

        rates.append(
            {"code": char_code, "name": name, "nominal": nominal, "value": value}
        )

    return rates


@router.get("/")
async def get_course(date_req=None):
    # xml_data = await get_cb("19/11/2025")
    xml_data = await get_cb(date_req)
    res = parse_xml(xml_data)
    return res


@router.get("/currency")
async def get_curr(name_val: str):
    xml_data = await get_cb("21/11/2025")
    if xml_data is None:
        return []
    root = ET.fromstring(xml_data)
    rates = []

    for valute in root.findall("Valute"):
        char_code = valute.findtext("CharCode")
        if char_code == name_val:
            name = valute.findtext("Name")
            nominal = valute.findtext("Nominal")
            value = valute.findtext("Value")

            rates.append(
                {"code": char_code, "name": name, "nominal": nominal, "value": value}
            )

    return rates


def get_history(currency_code="R01235", start="01/01/2020", end="01/01/2025"):
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


@router.get("/predict")
async def predict(days_ahead: int):
    model = joblib.load("currency_model.pkl")
    prediction = model.predict([[days_ahead]])[0]

    return {"predicted_rate": round(float(prediction), 2)}
