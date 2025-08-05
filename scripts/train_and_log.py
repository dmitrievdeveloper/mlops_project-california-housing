import mlflow
import mlflow.sklearn
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_and_log():
    logger.info("Starting model training and logging")
    # Configure MLflow and MinIO
    os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadminpassword"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
    
    mlflow.set_tracking_uri("http://mlflow-server:5000")

    # Load data
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame

    X = df.drop('MedHouseVal', axis=1)
    y = df['MedHouseVal']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)

    # Log to MLflow
    with mlflow.start_run():
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name="california_housing"
        )
        mlflow.log_metric("MAE", mae)
        mlflow.log_param("n_estimators", 100)

if __name__ == "__main__":
    train_and_log()
