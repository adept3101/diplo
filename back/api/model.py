import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import joblib

# загрузка данных
df = pd.read_csv("usd_history.csv")

# преобразуем дату в число
df["day"] = np.arange(len(df))

X = df[["day"]]
y = df["rate"]

model = LinearRegression()
model.fit(X, y)

# сохраняем модель
joblib.dump(model, "currency_model.pkl")
