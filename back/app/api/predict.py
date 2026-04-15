import joblib
import numpy as np
import tensorflow as tf
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/predict", tags=["USD"])

custom_objects = {
    'mse': tf.keras.losses.MeanSquaredError(),
}

model = tf.keras.models.load_model("usd_rate_lstm_improved.h5", custom_objects=custom_objects, compile=True)
feat_scaler = joblib.load("feature_scaler.pkl")
target_scaler = joblib.load("target_scaler.pkl")

@router.get("/course/predict")
async def predict(target_date: str):
    history_data = get_last_n_days_from_csv("usd_history.csv", n=60) #type: ignore
    
    scaled_data = feat_scaler.transform(history_data)
    X = np.expand_dims(scaled_data, axis=0) # Форма [1, 60, features]
    
    prediction_scaled = model.predict(X)
    
    prediction_real = target_scaler.inverse_transform(prediction_scaled)
    
    return {
        "target_date": target_date,
        "predicted_rate": float(prediction_real[0][0])
    }
