import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.impute import KNNImputer
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Dropout, Bidirectional
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Загрузка данных
data = pd.read_csv("usd_history.csv", encoding="latin-1")

# Предобработка данных
def preprocess_data(data):
    # Обработка дат
    data["date"] = pd.to_datetime(data["date"], dayfirst=True, errors="coerce")
    data = data.sort_values("date").reset_index(drop=True)
    
    # Удаление дубликатов
    data = data.drop_duplicates(subset=['date'])
    
    # Проверка пропусков
    print(f"Пропуски в rate: {data['rate'].isna().sum()}")
    
    # Создание полной временной шкалы
    full_date_range = pd.date_range(start=data['date'].min(), end=data['date'].max(), freq='D')
    data = data.set_index('date').reindex(full_date_range).rename_axis('date').reset_index()
    
    # Заполнение пропусков (интерполяция для временных рядов)
    data['rate'] = data['rate'].interpolate(method='linear', limit_direction='both')
    
    # Если остались пропуски, используем KNN
    if data['rate'].isna().sum() > 0:
        imputer = KNNImputer(n_neighbors=5)
        data['rate'] = imputer.fit_transform(data[['rate']])
    
    return data

data = preprocess_data(data)
print(f"Период: с {data['date'].min()} по {data['date'].max()}")
print(f"Всего записей: {len(data)}")

# Создание дополнительных признаков
def create_features(data):
    df = data.copy()
    
    # Временные признаки
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['quarter'] = df['date'].dt.quarter
    df['day_of_year'] = df['date'].dt.dayofyear
    
    # Технические индикаторы
    # Скользящие средние
    for window in [5, 10, 20, 50]:
        df[f'ma_{window}'] = df['rate'].rolling(window=window).mean()
        df[f'std_{window}'] = df['rate'].rolling(window=window).std()
    
    # Экспоненциальное сглаживание
    df['ema_12'] = df['rate'].ewm(span=12).mean()
    df['ema_26'] = df['rate'].ewm(span=26).mean()
    
    # RSI
    def calculate_rsi(data, periods=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    df['rsi'] = calculate_rsi(df['rate'])
    
    # Доходность
    df['return_1d'] = df['rate'].pct_change(1)
    df['return_5d'] = df['rate'].pct_change(5)
    df['return_20d'] = df['rate'].pct_change(20)
    
    # Волатильность
    df['volatility_10d'] = df['return_1d'].rolling(window=10).std()
    
    # Лаговые признаки
    for lag in [1, 2, 3, 5]:
        df[f'lag_{lag}'] = df['rate'].shift(lag)
    
    # Удаление NaN
    df = df.dropna().reset_index(drop=True)
    
    return df

# Создаем признаки
data_features = create_features(data)
print(f"Размер данных с признаками: {data_features.shape}")
print(f"Колонки: {data_features.columns.tolist()}")

# Подготовка данных для LSTM
def prepare_lstm_data(data, feature_columns, target_column, time_steps=10):
    # Масштабирование
    feature_scaler = StandardScaler()
    target_scaler = StandardScaler()
    
    scaled_features = feature_scaler.fit_transform(data[feature_columns])
    scaled_target = target_scaler.fit_transform(data[[target_column]])
    
    # Создание последовательностей
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(scaled_features[i:i + time_steps])
        y.append(scaled_target[i + time_steps])
    
    return np.array(X), np.array(y), feature_scaler, target_scaler

# Выбираем колонки для признаков
feature_columns = ['ma_5', 'ma_10', 'rsi', 'return_1d', 'volatility_10d', 
                   'day_of_week', 'month', 'lag_1']
target_column = 'rate'

time_steps = 20  # Увеличил окно для лучшего контекста
X, y, feature_scaler, target_scaler = prepare_lstm_data(
    data_features, feature_columns, target_column, time_steps
)

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")

# Разделение на train/val/test с учетом временного ряда
train_size = int(len(X) * 0.7)
val_size = int(len(X) * 0.15)
test_size = len(X) - train_size - val_size

X_train = X[:train_size]
y_train = y[:train_size]

X_val = X[train_size:train_size + val_size]
y_val = y[train_size:train_size + val_size]

X_test = X[train_size + val_size:]
y_test = y[train_size + val_size:]

print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

# Создание улучшенной модели
def create_improved_model(input_shape):
    model = Sequential([
        # Первый слой Bidirectional LSTM
        Bidirectional(LSTM(128, return_sequences=True), input_shape=input_shape),
        Dropout(0.3),
        
        # Второй слой LSTM
        LSTM(64, return_sequences=True),
        Dropout(0.3),
        
        # Третий слой LSTM
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        
        # Полносвязные слои
        Dense(16, activation='relu'),
        Dropout(0.2),
        Dense(8, activation='relu'),
        Dense(1)
    ])
    
    return model

model = create_improved_model((time_steps, len(feature_columns)))
model.summary()

# Компиляция
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='mse',
    metrics=['mae', 'mape']
)

# Callbacks
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.00001,
        verbose=1
    ),
    ModelCheckpoint(
        'best_model.h5',
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
]

# Обучение
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# Оценка модели
def evaluate_model(model, X_test, y_test, target_scaler):
    # Предсказания
    y_pred = model.predict(X_test)
    
    # Обратное масштабирование
    y_test_inv = target_scaler.inverse_transform(y_test)
    y_pred_inv = target_scaler.inverse_transform(y_pred)
    
    # Метрики
    mse = mean_squared_error(y_test_inv, y_pred_inv)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test_inv, y_pred_inv)
    r2 = r2_score(y_test_inv, y_pred_inv)
    mape = np.mean(np.abs((y_test_inv - y_pred_inv) / y_test_inv)) * 100
    
    print(f"MSE: {mse:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"MAE: {mae:.6f}")
    print(f"R2 Score: {r2:.6f}")
    print(f"MAPE: {mape:.2f}%")
    
    return y_test_inv, y_pred_inv

y_test_inv, y_pred_inv = evaluate_model(model, X_test, y_test, target_scaler)

# Визуализация результатов
def plot_results(history, y_test_inv, y_pred_inv, data_features, time_steps):
    fig, axes = plt.subplots(3, 2, figsize=(18, 15))
    
    # График потерь
    axes[0, 0].plot(history.history['loss'], label='Train Loss')
    axes[0, 0].plot(history.history['val_loss'], label='Validation Loss')
    axes[0, 0].set_title('Model Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # График MAE
    axes[0, 1].plot(history.history['mae'], label='Train MAE')
    axes[0, 1].plot(history.history['val_mae'], label='Validation MAE')
    axes[0, 1].set_title('Model MAE')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('MAE')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # График предсказаний vs фактические
    axes[1, 0].plot(y_test_inv, label='Actual', alpha=0.7)
    axes[1, 0].plot(y_pred_inv, label='Predicted', alpha=0.7)
    axes[1, 0].set_title('Actual vs Predicted Exchange Rates')
    axes[1, 0].set_xlabel('Time Step')
    axes[1, 0].set_ylabel('Rate')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Разброс предсказаний
    axes[1, 1].scatter(y_test_inv, y_pred_inv, alpha=0.5)
    axes[1, 1].plot([y_test_inv.min(), y_test_inv.max()], 
                     [y_test_inv.min(), y_test_inv.max()], 'r--', lw=2)
    axes[1, 1].set_title('Prediction Scatter Plot')
    axes[1, 1].set_xlabel('Actual Values')
    axes[1, 1].set_ylabel('Predicted Values')
    axes[1, 1].grid(True)
    
    # Распределение ошибок
    errors = y_test_inv.flatten() - y_pred_inv.flatten()
    axes[2, 0].hist(errors, bins=50, edgecolor='black')
    axes[2, 0].set_title('Error Distribution')
    axes[2, 0].set_xlabel('Error')
    axes[2, 0].set_ylabel('Frequency')
    axes[2, 0].grid(True)
    
    # Исторические данные с прогнозом
    test_dates = data_features['date'].iloc[-(len(y_test_inv)):].values
    axes[2, 1].plot(test_dates, y_test_inv, label='Actual', alpha=0.7)
    axes[2, 1].plot(test_dates, y_pred_inv, label='Predicted', alpha=0.7)
    axes[2, 1].set_title('Test Period Predictions')
    axes[2, 1].set_xlabel('Date')
    axes[2, 1].set_ylabel('Rate')
    axes[2, 1].legend()
    axes[2, 1].grid(True)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()

plot_results(history, y_test_inv, y_pred_inv, data_features, time_steps)

# Функция для прогнозирования будущих значений
def predict_future(model, last_sequence, n_days, feature_scaler, target_scaler, 
                   feature_columns, time_steps):
    """
    Прогнозирование на n_days вперед
    """
    current_sequence = last_sequence.copy()
    predictions = []
    
    for i in range(n_days):
        # Предсказание следующего значения
        next_pred = model.predict(current_sequence.reshape(1, time_steps, len(feature_columns)), 
                                  verbose=0)
        predictions.append(next_pred[0, 0])
        
        # Обновление последовательности (сдвиг и добавление нового предсказания)
        # Здесь нужно обновить все признаки для следующего шага
        # Это упрощенная версия, в реальности нужно пересчитывать все признаки
        current_sequence = np.roll(current_sequence, -1, axis=0)
        # Обновляем только target, остальные признаки остаются как были
        # В реальности нужно пересчитывать все признаки
    
    # Обратное масштабирование
    predictions = np.array(predictions).reshape(-1, 1)
    predictions_inv = target_scaler.inverse_transform(predictions)
    
    return predictions_inv.flatten()

# Получение последней последовательности для прогноза
last_sequence = X_test[-1]  # Используем последний тестовый семпл
future_days = 30
future_predictions = predict_future(
    model, last_sequence, future_days, feature_scaler, 
    target_scaler, feature_columns, time_steps
)

# Визуализация будущего прогноза
def plot_future_forecast(data_features, y_test_inv, future_predictions, future_days):
    plt.figure(figsize=(15, 8))
    
    # Исторические данные (последние 100 дней)
    historical_dates = data_features['date'].iloc[-100:].values
    historical_rates = data_features['rate'].iloc[-100:].values
    
    plt.plot(historical_dates, historical_rates, 
             label='Historical Data', linewidth=2, color='blue')
    
    # Тестовые предсказания (последние 30 дней)
    test_dates = data_features['date'].iloc[-(len(y_test_inv)):].values
    plt.plot(test_dates, y_test_inv, 
             label='Test Actual', alpha=0.7, color='green')
    plt.plot(test_dates, y_pred_inv, 
             label='Test Predicted', alpha=0.7, color='orange')
    
    # Будущий прогноз
    last_date = data_features['date'].iloc[-1]
    future_dates = [last_date + timedelta(days=i+1) for i in range(future_days)]
    plt.plot(future_dates, future_predictions, 
             label='Future Forecast', linestyle='--', linewidth=2, color='red')
    
    plt.title(f'USD Exchange Rate Forecast - Next {future_days} Days')
    plt.xlabel('Date')
    plt.ylabel('Rate')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # Вывод прогноза
    print(f"\nПрогноз на следующие {future_days} дней:")
    for i, (date, pred) in enumerate(zip(future_dates, future_predictions), 1):
        print(f"  {date.strftime('%Y-%m-%d')}: {pred:.4f}")
    
    # Статистика прогноза
    print(f"\nСтатистика прогноза:")
    print(f"  Среднее: {future_predictions.mean():.4f}")
    print(f"  Минимум: {future_predictions.min():.4f}")
    print(f"  Максимум: {future_predictions.max():.4f}")
    print(f"  Стандартное отклонение: {future_predictions.std():.4f}")

plot_future_forecast(data_features, y_test_inv, future_predictions, future_days)

# Сохранение модели и скейлеров
model.save('usd_rate_lstm_improved.h5')
import joblib
joblib.dump(feature_scaler, 'feature_scaler.pkl')
joblib.dump(target_scaler, 'target_scaler.pkl')

# Функция для загрузки и использования модели
def load_and_predict(model_path, feature_scaler_path, target_scaler_path, 
                     last_sequence, n_days, feature_columns, time_steps):
    """
    Загрузка сохраненной модели и прогнозирование
    """
    model = load_model(model_path)
    feature_scaler = joblib.load(feature_scaler_path)
    target_scaler = joblib.load(target_scaler_path)
    
    predictions = predict_future(
        model, last_sequence, n_days, feature_scaler, 
        target_scaler, feature_columns, time_steps
    )
    
    return predictions

# Пример использования загрузки модели
# predictions = load_and_predict(
#     'usd_rate_lstm_improved.h5', 
#     'feature_scaler.pkl', 
#     'target_scaler.pkl',
#     last_sequence, 
#     30, 
#     feature_columns, 
#     time_steps
# )
