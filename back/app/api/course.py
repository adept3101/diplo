from fastapi import APIRouter, HTTPException, Query
import xml.etree.ElementTree as ET
import httpx
from datetime import datetime

router = APIRouter(prefix="/course", tags=["Course"])
client = httpx.AsyncClient()

def clean_value(value_str: str) -> float:
    try:
        return float(value_str.replace(',', '.'))
    except (ValueError, AttributeError):
        return 0.0


async def get_cb(date_req=None):
    params = {"date_req": date_req} if date_req else {}
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    
    try:
        response = await client.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"CBR service unavailable: {e}")


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
    xml_data = await get_cb(date_req)
    res = parse_xml(xml_data)
    return res


# @router.get("/currency")
# async def get_curr(name_val: str, date_req: str):
#     xml_data = await get_cb(date_req)
#     if not xml_data:
#         raise HTTPException(status_code=404, detail="No data from CBR")
#
#     root = ET.fromstring(xml_data)
#
#     for valute in root.findall("Valute"):
#         char_code = valute.findtext("CharCode")
#
#         # Сравниваем код валюты (приводим к верхнему регистру для надежности)
#         if char_code and char_code.upper() == name_val.upper():
#             # Извлекаем сырые строки
#             raw_value = valute.findtext("Value")
#             raw_nominal = valute.findtext("Nominal")
#             raw_name = valute.findtext("Name")
#
#             # Проверка: если вдруг ЦБ прислал пустой тег (защита от None)
#             if raw_value is None:
#                 raise HTTPException(status_code=500, detail="Value field is missing in XML")
#
#             return {
#                 "code": char_code,
#                 "name": raw_name or "Unknown",
#                 "nominal": int(raw_nominal) if raw_nominal else 1,
#                 "value": clean_value(raw_value), # Теперь сюда попадает только str
#                 "date": date_req or datetime.now().strftime("%d/%m/%Y")
#             }
#
#     raise HTTPException(status_code=404, detail="Currency not found")

@router.get("/currency")
async def get_currency(
    date_req: str = Query(..., description="Format: dd/mm/yyyy"),
    name_val: str = Query(..., description="Currency code, e.g. USD")
):
    xml_data = await get_cb(date_req)
    all_rates = parse_xml(xml_data)
    
    # Фильтруем по коду (USD, EUR и т.д.)
    filtered = [r for r in all_rates if r["code"] == name_val]
    
    if not filtered:
        # Если данных на дату нет (выходные), фронтенд делает Forward Fill, 
        # так что возвращаем пустой массив или 404
        return []
        
    return filtered

@router.get("/history")
async def get_currency_history(name_val: str, date_from: str, date_to: str):
    all_rates_xml = await get_cb(date_to)
    root_all = ET.fromstring(all_rates_xml)
    valute_id = None
    for v in root_all.findall("Valute"):
        if v.findtext("CharCode") == name_val.upper():
            valute_id = v.get("ID")
            break
            
    if not valute_id:
        raise HTTPException(status_code=404, detail="Currency ID not found")

    # Запрос динамики курса
    url = f"https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date_from}&date_req2={date_to}&VAL_NM_RQ={valute_id}"
    response = await client.get(url)
    root = ET.fromstring(response.text)
    
    history = []
    for record in root.findall("Record"):
        history.append({
            "date": record.get("Date"),
            "value": clean_value(record.findtext("Value")), #type: ignore
            "nominal": int(record.findtext("Nominal") or 1)
        })
    return history
