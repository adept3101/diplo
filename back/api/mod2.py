import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib.pyplot as plt

df = pd.read_csv("usd_history.csv")

df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", dayfirst=True)
df = df.sort_values("date").reset_index(drop=True)

df["dayofweek"] = df["date"].dt.dayofweek
df["month"] = df["date"].dt.month
df["dayofmonth"] = df["date"].dt.day
df["quarter"] = df["date"].dt.quarter

df["lag1"] = df["rate"].shift(1)
df["lag2"] = df["rate"].shift(2)
df["lag3"] = df["rate"].shift(3)
df["lag7"] = df["rate"].shift(7)
df["lag14"] = df["rate"].shift(14)

df["ma7"] = df["rate"].rolling(7).mean()
df["ma14"] = df["rate"].rolling(14).mean()
df["ma30"] = df["rate"].rolling(30).mean()

df["volatility_7"] = df["rate"].rolling(7).std()
df["volatility_14"] = df["rate"].rolling(14).std()

df["pct_change_1"] = df["rate"].pct_change(1)
df["pct_change_7"] = df["rate"].pct_change(7)

df = df.dropna().reset_index(drop=True)

train_size = len(df) - 30
train = df.iloc[:train_size]
test = df.iloc[train_size:]

features = [
    "dayofweek", "month", "dayofmonth", "quarter",
    "lag1", "lag2", "lag3", "lag7", "lag14",
    "ma7", "ma14", "ma30",
    "volatility_7", "volatility_14",
    "pct_change_1", "pct_change_7"
]

X_train = train[features].values
y_train = train["rate"].values
X_test = test[features].values
y_test = test["rate"].values

scaler_X = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

scaler_y = StandardScaler()
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

def create_sequences(X, y, sequence_length=10):
    X_seq, y_seq = [], []
    for i in range(len(X) - sequence_length):
        X_seq.append(X[i:i+sequence_length])
        y_seq.append(y[i+sequence_length])
    return np.array(X_seq), np.array(y_seq)

sequence_length = 10
X_train_seq, y_train_seq = create_sequences(X_train_scaled, y_train_scaled, sequence_length)
X_test_seq, y_test_seq = create_sequences(X_test_scaled, y_test_scaled, sequence_length)

# print(f"Размерность обучающих данных: {X_train_seq.shape}")
# print(f"Размерность тестовых данных: {X_test_seq.shape}")

def create_model(input_shape):
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        
        layers.LSTM(64, return_sequences=True, dropout=0.2),
        layers.LSTM(32, dropout=0.2),
        
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(16, activation='relu'),
        layers.Dropout(0.2),
        
        layers.Dense(1)
    ])
    
    return model

model = create_model((sequence_length, X_train_seq.shape[2]))

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='mse',
    metrics=['mae', 'mape']
)

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=20,
        restore_best_weights=True
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=10,
        min_lr=0.00001
    )
]

history = model.fit(
    X_train_seq, y_train_seq,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

y_pred_scaled = model.predict(X_test_seq)
y_pred = scaler_y.inverse_transform(y_pred_scaled).flatten()

y_test_for_compare = y_test[sequence_length:]

# print("\n" + "="*50)
# print("РЕЗУЛЬТАТЫ ПРОГНОЗИРОВАНИЯ")
# print("="*50)
# print("\nПоследние реальные значения:")
print(y_test_for_compare[-10:])

print("\nПрогноз модели:")
print(y_pred[-10:])

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_test_for_compare, y_pred)
rmse = np.sqrt(mean_squared_error(y_test_for_compare, y_pred))
r2 = r2_score(y_test_for_compare, y_pred)

# print(f"\nМетрики модели:")
# print(f"MAE: {mae:.4f}")
# print(f"RMSE: {rmse:.4f}")
# print(f"R² Score: {r2:.4f}")

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Обучающая')
plt.plot(history.history['val_loss'], label='Валидационная')
plt.title('Функция потерь (MSE)')
plt.xlabel('Эпоха')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(y_test_for_compare, label='Реальные значения', marker='o')
plt.plot(y_pred, label='Прогноз', marker='s')
plt.title('Сравнение прогноза с реальными значениями')
plt.xlabel('Время')
plt.ylabel('Курс')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

model.save("currency_model_nn.h5")
joblib.dump(scaler_X, "scaler_X.pkl")
joblib.dump(scaler_y, "scaler_y.pkl")


def predict_future(model, last_sequence, scaler_X, scaler_y, n_days=7):
    predictions = []
    current_sequence = last_sequence.copy()
    
    for _ in range(n_days):
        # Предсказание следующего значения
        pred_scaled = model.predict(current_sequence[np.newaxis, ...], verbose=0)
        pred = scaler_y.inverse_transform(pred_scaled)[0, 0]
        predictions.append(pred)
        
        # Обновление последовательности для следующего предсказания
        # (в реальном приложении нужно также обновить другие признаки)
        new_row = current_sequence[-1].copy()
        # Здесь должна быть логика обновления всех признаков
        current_sequence = np.vstack([current_sequence[1:], new_row])
    
    return predictions

# Пример использования функции предсказания
last_seq = X_test_seq[-1]
future_predictions = predict_future(model, last_seq, scaler_X, scaler_y, n_days=7)
print(f"\nПрогноз на следующие 7 дней: {future_predictions}")
