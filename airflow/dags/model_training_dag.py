from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def train_model():
    try:
        result = subprocess.run(
            ['python', '/opt/airflow/scripts/train_and_log.py'],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        raise

with DAG(
    'model_training',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )
