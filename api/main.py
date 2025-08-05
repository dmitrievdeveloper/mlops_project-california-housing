from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.sklearn
import os
from dotenv import load_dotenv
import time
from typing import Optional

app = FastAPI()
load_dotenv()

model = None
model_loaded = False
last_load_attempt = 0

class HousingFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

def load_model():
    global model, model_loaded, last_load_attempt
    try:
        os.environ.update({
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "MLFLOW_S3_ENDPOINT_URL": os.getenv("MLFLOW_S3_ENDPOINT_URL")
        })
        
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        model = mlflow.sklearn.load_model(
            "models:/california_housing/latest",
            dst_path="/tmp/model"
        )
        model_loaded = True
    except Exception as e:
        model_loaded = False
        print(f"Model loading failed: {e}")
    finally:
        last_load_attempt = time.time()

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/health")
async def health_check():
    if model_loaded:
        return {"status": "healthy", "model_loaded": True}
    else:
        return {"status": "degraded", "model_loaded": False}

@app.post("/predict")
async def predict(features: HousingFeatures):
    if not model_loaded:
        if time.time() - last_load_attempt > 300:
            load_model()
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please try again later."
        )
    
    try:
        prediction = model.predict([[
            features.MedInc, features.HouseAge, features.AveRooms,
            features.AveBedrms, features.Population, features.AveOccup,
            features.Latitude, features.Longitude
        ]])
        return {"prediction": float(prediction[0])}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
