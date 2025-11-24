from fastapi import FastAPI
import requests
import xml.etree.ElementTree as ET

app = FastAPI()


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

# @app.get("/")
# async def get_course():
#     xml_data = get_cb("19/11/2025")
#     return xml_data
    # rates = parse_xml(xml_data)
    # for r in rates:
    #     return f"{r['code']}: {r['value']} руб."

@app.get("/")
async def get_course():
    xml_data = await get_cb("19/11/2025")
    res = parse_xml(xml_data)
    return res


@app.get("/currency")
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


# xml_data = get_cb("19/11/2025")
# # print(xml_data)
# print("\n")
#
# rates = parse_xml(xml_data)
# for r in rates:
#     print(f"{r['code']}: {r['value']} руб.")
