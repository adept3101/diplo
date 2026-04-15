from fastapi import APIRouter, HTTPException, Query
import xml.etree.ElementTree as ET
import httpx
from datetime import datetime, timedelta
import tensorflow as tf
import joblib
import numpy as np
import pandas as pd

router = APIRouter(prefix="/course", tags=["Course"])
client = httpx.AsyncClient()


# ── Утилиты ───────────────────────────────────────────────────────────────────

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
        rates.append({"code": char_code, "name": name, "nominal": nominal, "value": value})
    return rates


# ── ML: подготовка фичей ──────────────────────────────────────────────────────

def get_last_n_days_from_csv(file_path: str, n: int) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df.tail(n)


RSI_PERIOD = 14  # период RSI — должен совпадать с тем, что был при обучении


def _calc_rsi(prices: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """Классический RSI Wilder'а."""
    delta  = prices.diff()
    gain   = delta.clip(lower=0)
    loss   = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs  = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # нейтральное значение для первых точек


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Строит признаки в том же порядке, что использовался при обучении feat_scaler:
        day_of_week, month, lag_1, ma_5, ma_10, return_1d, rsi, volatility_10d

    Проверить порядок: print(feat_scaler.feature_names_in_)
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    df = df.sort_values('date').reset_index(drop=True)

    df['day_of_week']   = df['date'].dt.dayofweek
    df['month']         = df['date'].dt.month
    df['lag_1']         = df['rate'].shift(1)
    df['ma_5']          = df['rate'].rolling(window=5).mean()
    df['ma_10']         = df['rate'].rolling(window=10).mean()
    df['return_1d']     = df['rate'].pct_change()           # (rate - lag_1) / lag_1
    df['rsi']           = _calc_rsi(df['rate'], RSI_PERIOD)
    df['volatility_10d'] = df['rate'].rolling(window=10).std()

    df = df.dropna()

    # Порядок СТРОГО как при fit скалера (feat_scaler.feature_names_in_)
    feature_cols = ['ma_5', 'ma_10', 'rsi', 'return_1d', 'volatility_10d', 'day_of_week', 'month', 'lag_1']
    return df[feature_cols]


def build_next_row(window_df: pd.DataFrame, pred_rate: float, next_date: datetime) -> pd.DataFrame:
    """
    Формирует строку признаков для следующего шага рекурсивного прогноза.
    window_df — текущее окно признаков (содержит колонку lag_1 как прокси для курса).
    """
    # Восстанавливаем ряд курсов из lag_1 + последнего предсказания
    # lag_1[i] = rate[i-1], поэтому rates = lag_1.tolist() + [pred_rate]
    prev_rates = list(window_df['lag_1'].values) + [pred_rate]
    # Последние значения для скользящих
    recent_10  = prev_rates[-10:]
    recent_5   = prev_rates[-5:]

    lag_1        = prev_rates[-2]                        # предпоследний курс
    ma_5         = float(np.mean(recent_5))
    ma_10        = float(np.mean(recent_10))
    return_1d    = (pred_rate - lag_1) / lag_1 if lag_1 != 0 else 0.0
    volatility   = float(np.std(recent_10, ddof=1)) if len(recent_10) >= 2 else 0.0

    # RSI: берём последние RSI из окна и досчитываем один шаг (упрощённо)
    last_rsi     = float(window_df['rsi'].iloc[-1])
    delta        = pred_rate - lag_1
    # Один шаг EWM-RSI: alpha = 1 / RSI_PERIOD
    alpha        = 1.0 / RSI_PERIOD
    last_gain    = max(delta, 0)
    last_loss    = max(-delta, 0)
    prev_gain    = (last_rsi / 100) * (100 - last_rsi) if last_rsi != 100 else 0
    new_avg_gain = alpha * last_gain + (1 - alpha) * prev_gain
    new_avg_loss = alpha * last_loss + (1 - alpha) * max((100 - last_rsi) / 100 * last_rsi, 0)
    rs           = new_avg_gain / new_avg_loss if new_avg_loss != 0 else 100
    new_rsi      = float(100 - 100 / (1 + rs))

    new_row = {
        'ma_5':           ma_5,
        'ma_10':          ma_10,
        'rsi':            new_rsi,
        'return_1d':      return_1d,
        'volatility_10d': volatility,
        'day_of_week':    next_date.weekday(),
        'month':          next_date.month,
        'lag_1':          lag_1,
    }
    return pd.DataFrame([new_row])


# ── Загрузка модели ───────────────────────────────────────────────────────────

custom_objects = {
    'mse': tf.keras.losses.MeanSquaredError(),
}

model        = tf.keras.models.load_model("usd_rate_lstm_improved.h5", custom_objects=custom_objects, compile=True)
feat_scaler  = joblib.load("feature_scaler.pkl")
target_scaler = joblib.load("target_scaler.pkl")


# ── Эндпоинты ─────────────────────────────────────────────────────────────────

@router.get("/predict")
async def predict(
    days: int = Query(7, ge=1, le=90, description="Горизонт прогноза в днях (1–90)"),
    name_val: str = Query("USD", description="Код валюты, например USD, EUR, CNY"),
):
    """
    Рекурсивный прогноз курса валюты на N дней вперёд.

    Алгоритм:
    1. Читает историю из {name_val}_history.csv (нужно 80+ строк).
    2. Строит признаки (prepare_features).
    3. На каждом шаге: масштабирует окно → прогноз → добавляет в окно (recursive forecasting).
    """
    csv_path = f"{name_val.upper()}_history.csv"

    try:
        history_raw = get_last_n_days_from_csv(csv_path, n=80)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Файл истории не найден: {csv_path}. "
                   f"Убедитесь, что файл существует рядом с сервером."
        )

    if len(history_raw) < 15:
        raise HTTPException(
            status_code=422,
            detail=f"Недостаточно данных в {csv_path}: нужно минимум 15 строк, найдено {len(history_raw)}."
        )

    processed_df = prepare_features(history_raw)

    if len(processed_df) < 60:
        raise HTTPException(
            status_code=422,
            detail=f"После обработки признаков осталось {len(processed_df)} строк — нужно минимум 60 для LSTM окна."
        )

    # Берём последние 60 точек как стартовое окно для модели
    WINDOW = 60
    current_input = processed_df.tail(WINDOW).reset_index(drop=True)

    # Дата последней известной записи (для сдвига дат прогноза)
    last_date = pd.to_datetime(history_raw['date'].iloc[-1], format='%d.%m.%Y')

    forecast_results = []

    for i in range(days):
        # 1. Масштабируем окно
        scaled_input = feat_scaler.transform(current_input)
        X = np.expand_dims(scaled_input, axis=0)  # shape: (1, 60, n_features)

        # 2. Предсказываем
        pred_scaled = model.predict(X, verbose=0)
        pred_real   = float(target_scaler.inverse_transform(pred_scaled)[0][0])

        # 3. Дата следующего шага
        next_date = last_date + timedelta(days=i + 1)

        forecast_results.append({
            "date":           next_date.strftime("%Y-%m-%d"),
            "predicted_rate": round(pred_real, 4),
        })

        # 4. Обновляем окно: сдвигаем на 1 шаг вперёд, добавляем новую строку с пересчитанными фичами
        new_row     = build_next_row(current_input, pred_real, next_date)
        current_input = pd.concat(
            [current_input.iloc[1:], new_row],
            ignore_index=True
        )

    return forecast_results


@router.get("/")
async def get_course(date_req=None):
    xml_data = await get_cb(date_req)
    return parse_xml(xml_data)


@router.get("/currency")
async def get_currency(
    date_req: str = Query(..., description="Формат: dd/mm/yyyy"),
    name_val: str = Query(..., description="Код валюты, например USD"),
):
    xml_data  = await get_cb(date_req)
    all_rates = parse_xml(xml_data)
    filtered  = [r for r in all_rates if r["code"] == name_val.upper()]
    return filtered if filtered else []


@router.get("/history")
async def get_currency_history(name_val: str, date_from: str, date_to: str):
    all_rates_xml = await get_cb(date_to)
    root_all  = ET.fromstring(all_rates_xml)
    valute_id = None

    for v in root_all.findall("Valute"):
        if v.findtext("CharCode") == name_val.upper():
            valute_id = v.get("ID")
            break

    if not valute_id:
        raise HTTPException(status_code=404, detail=f"Валюта '{name_val}' не найдена в ответе ЦБ РФ.")

    url      = (f"https://www.cbr.ru/scripts/XML_dynamic.asp"
                f"?date_req1={date_from}&date_req2={date_to}&VAL_NM_RQ={valute_id}")
    response = await client.get(url)
    root     = ET.fromstring(response.text)

    history = []
    for record in root.findall("Record"):
        history.append({
            "date":    record.get("Date"),
            "value":   clean_value(record.findtext("Value")),  # type: ignore
            "nominal": int(record.findtext("Nominal") or 1),
        })
    return history
