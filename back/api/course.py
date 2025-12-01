from fastapi import FastAPI, APIRouter
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import joblib
from typing import List
import pandas as pd
import joblib
from datetime import datetime, timedelta

router = APIRouter(prefix="/course", tags=["Course"])


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
async def get_curr(date_req, name_val: str):
    xml_data = await get_cb(date_req)
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


# xml_data = get_history()

# data = parse_history(xml_data)
# df = pd.DataFrame(data, columns=["date", "rate"])  # type: ignore
# df.to_csv("usd_history.csv", index=False)


@router.get("/predict")
async def predict(target_date: str):
    model = joblib.load("api/currency_model_boost.pkl")

    df = pd.read_csv("usd_history.csv")
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", dayfirst=True)
    df = df.sort_values("date").reset_index(drop=True)

    try:
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    last_known_date = df["date"].iloc[-1]

    if target_date <= last_known_date:
        value = df.loc[df["date"] == target_date]
        if not value.empty:
            return {"predicted_rate": round(float(value["rate"].iloc[0]), 2)}
        else:
            return {"error": "Date exists in past but not found in dataset"}

    days_ahead = (target_date - last_known_date).days

    # Начальное состояние
    last = df.iloc[-1].copy()

    # Пошаговое прогнозирование
    for i in range(days_ahead):
        next_date = last["date"] + timedelta(days=1)

        dayofweek = next_date.dayofweek
        month = next_date.month

        lag1 = last["rate"]
        lag2 = df.iloc[-2]["rate"]
        lag7 = df.iloc[-7]["rate"]

        ma7 = df["rate"].rolling(7).mean().iloc[-1]
        ma30 = df["rate"].rolling(30).mean().iloc[-1]

        X = [[dayofweek, month, lag1, lag2, lag7, ma7, ma30]]

        future_rate = model.predict(X)[0]

        df.loc[len(df)] = {"date": next_date, "rate": future_rate}
        last = df.iloc[-1]

    return {
        "predicted_rate": round(float(future_rate), 2),
        "date": target_date.strftime("%Y-%m-%d"),
    }
