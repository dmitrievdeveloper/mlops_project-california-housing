FROM apache/airflow:2.8.1-python3.9

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*
 
USER airflow
RUN pip install --no-cache-dir \
    evidently pandas scikit-learn mlflow sqlalchemy psycopg2-binary \
    boto3 minio scipy numpy

COPY --chown=airflow:root ./airflow/dags/ /opt/airflow/dags/
COPY --chown=airflow:root ./scripts/ /opt/airflow/scripts/
