import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.impute import KNNImputer
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from keras.callbacks import EarlyStopping
from keras.optimizers import RMSprop
import tensorflow as tf

data = pd.read_csv("usd_history.csv", encoding="latin-1")

data["date"] = pd.to_datetime(data["date"], dayfirst=True, errors="coerce")
data = data.sort_values("date")  # Сортируем по дате

# Проверим, есть ли некорректные даты
# print(f"Всего строк: {len(data)}")
# print(f"Некорректных дат: {data['date'].isna().sum()}")

# Если есть некорректные даты, можно их удалить или исправить
if data["date"].isna().sum() > 0:
    # print("Некорректные строки:")
    # print(data[data["date"].isna()])
    data = data.dropna(subset=["date"])

# Обработка пропущенных значений в rate
# print(f"Пропущенных значений в rate: {data['rate'].isna().sum()}")

# Заполняем пропуски
if data["rate"].isna().sum() > 0:
    mode_value = (
        data["rate"].mode()[0] if not data["rate"].mode().empty else data["rate"].mean()
    )
    data["rate"].fillna(mode_value, inplace=True)

# Дополнительная обработка KNN если все еще есть пропуски
if data["rate"].isna().sum() > 0:
    imputer = KNNImputer(n_neighbors=5)
    data["rate"] = imputer.fit_transform(data[["rate"]])

# Проверим данные
# print(f"\nДиапазон дат: от {data['date'].min()} до {data['date'].max()}")
# print(f"Количество дней: {(data['date'].max() - data['date'].min()).days}")
# print(
#     f"Пропущенных дат: {pd.date_range(start=data['date'].min(), end=data['date'].max()).difference(data['date']).shape[0]}"
# )


# Подготовка данных для LSTM
def create_sequences(data, sequence_length):
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i : i + sequence_length])
        y.append(data[i + sequence_length])
    return np.array(X), np.array(y)


# Масштабирование данных
scaler = StandardScaler()
scaled_data = scaler.fit_transform(data[["rate"]].values)

# Создание последовательностей
time_steps = 10
X, y = create_sequences(scaled_data.flatten(), time_steps)


# Разделение на обучающую и тестовую выборки
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


# Изменение формы для LSTM (samples, time_steps, features)
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Создание модели
model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape=(time_steps, 1)))
model.add(LSTM(64, return_sequences=True))
model.add(LSTM(32))
model.add(Dense(1))

# Компиляция модели
optimizer = RMSprop(learning_rate=0.001)
model.compile(optimizer=optimizer, loss="mse", metrics=["mae"])

# Early stopping
early_stopping = EarlyStopping(
    monitor="val_loss", patience=10, restore_best_weights=True, verbose=1
)

# Обучение модели
history = model.fit(
    X_train,
    y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.1,
    verbose=1,
    callbacks=[early_stopping],
)

# Предсказания
y_pred = model.predict(X_test)

# Обратное масштабирование для оценки
y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
y_pred_inv = scaler.inverse_transform(y_pred)

# Вычисление метрик
mse = mean_squared_error(y_test_inv, y_pred_inv)
mae = mean_absolute_error(y_test_inv, y_pred_inv)
print(f"MSE: {mse:.6f}")
print(f"RMSE: {np.sqrt(mse):.6f}")
print(f"MAE: {mae:.6f}")

# Визуализация
plt.figure(figsize=(15, 10))

# График потерь
plt.subplot(2, 2, 1)
plt.plot(history.history["loss"][1:], label="Train Loss")
plt.plot(history.history["val_loss"][1:], label="Validation Loss")
plt.title("Training and Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)

# График MAE
plt.subplot(2, 2, 2)
plt.plot(history.history["mae"][1:], label="Train MAE")
plt.plot(history.history["val_mae"][1:], label="Validation MAE")
plt.title("Training and Validation MAE")
plt.xlabel("Epochs")
plt.ylabel("MAE")
plt.legend()
plt.grid(True)

# График предсказаний
plt.subplot(2, 1, 2)
plt.plot(y_test_inv, label="Actual", alpha=0.7, linewidth=2)
plt.plot(y_pred_inv, label="Predicted", alpha=0.7, linewidth=2)
plt.title("Actual vs Predicted Exchange Rates")
plt.xlabel("Time")
plt.ylabel("Rate")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# График исходных данных
plt.figure(figsize=(15, 5))
plt.plot(data["date"], data["rate"], label="Historical Rate", alpha=0.7)
plt.title("Historical USD Exchange Rate")
plt.xlabel("Date")
plt.ylabel("Rate")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()


# Прогноз на будущее
def forecast_future(model, last_sequence, steps_ahead, scaler, time_steps):
    predictions = []
    current_sequence = last_sequence.copy()

    for _ in range(steps_ahead):
        # Предсказание следующего значения
        pred = model.predict(current_sequence.reshape(1, time_steps, 1), verbose=0)
        predictions.append(pred[0, 0])

        # Обновление последовательности
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = pred

    return np.array(predictions)


# Пример использования прогноза
if len(X_test) > 0:
    last_sequence = X_test[-1].flatten()
    future_predictions = forecast_future(model, last_sequence, 5, scaler, time_steps)
    future_predictions_inv = scaler.inverse_transform(future_predictions.reshape(-1, 1))

    print(f"\nПрогноз на следующие 5 дней:")
    for i, pred in enumerate(future_predictions_inv.flatten(), 1):
        print(f"  День {i}: {pred:.4f}")

    # Сохранение модели
    model.save("usd_rate_lstm_model.h5")
