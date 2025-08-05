FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    mlflow[sqlalchemy,s3] \
    boto3 \
    psycopg2-binary

CMD ["sh", "-c", "mlflow server --backend-store-uri postgresql://mlflow_user:mlflow_password@postgres_mlflow/mlflow_db --default-artifact-root s3://mlflow/ --host 0.0.0.0"]
