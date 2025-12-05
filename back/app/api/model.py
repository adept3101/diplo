import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
import joblib

df = pd.read_csv("usd_history.csv")

# df["date"] = pd.to_datetime(df["date"])

df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", dayfirst=True)
df = df.sort_values("date").reset_index(drop=True)

df["dayofweek"] = df["date"].dt.dayofweek
df["month"] = df["date"].dt.month

df["lag1"] = df["rate"].shift(1)
df["lag2"] = df["rate"].shift(2)
df["lag7"] = df["rate"].shift(7)

df["ma7"] = df["rate"].rolling(7).mean()
df["ma30"] = df["rate"].rolling(30).mean()

df = df.dropna().reset_index(drop=True)

train = df.iloc[:-30]  # всё, кроме последних 30 дней
test = df.iloc[-30:]  # последние 30 дней

features = ["dayofweek", "month", "lag1", "lag2", "lag7", "ma7", "ma30"]

X_train = train[features]
y_train = train["rate"]

X_test = test[features]
y_test = test["rate"]

model = CatBoostRegressor(
    iterations=1000, depth=6, learning_rate=0.03, loss_function="RMSE", silent=True
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print("Последние реальные значения:")
print(y_test.values)

print("\nПрогноз модели:")
print(pred)

joblib.dump(model, "currency_model_boost.pkl")

print("\nМодель успешно сохранена: currency_model_boost.pkl")
