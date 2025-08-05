from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import subprocess

# Thresholds
MAE_THRESHOLD = 0.5

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_metrics():
    # Generate Evidently report
    subprocess.run(['python', '/opt/airflow/dags/../scripts/generate_evidently_report.py'], check=True)
    
    # In production, parse the report or get metrics from MLflow
    # For demo, we'll just check if report was generated
    try:
        with open('/tmp/evidently_report.html', 'r') as f:
            return True  # Simplified check
    except:
        return False

def decide_retraining(**context):
    if check_metrics():
        print("Metrics check passed threshold. Triggering retraining.")
        return 'trigger_retraining'
    else:
        print("Metrics within acceptable range. No retraining needed.")
        return 'do_nothing'

with DAG(
    'model_monitoring',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:

    check_metrics_task = PythonOperator(
        task_id='check_metrics',
        python_callable=decide_retraining,
        provide_context=True,
    )

    trigger_retraining = TriggerDagRunOperator(
        task_id='trigger_retraining',
        trigger_dag_id='model_training',
        wait_for_completion=False,
        reset_dag_run=True,
    )

    do_nothing_task = PythonOperator(
        task_id='do_nothing',
        python_callable=lambda: print("No action required"),
    )

    check_metrics_task >> [trigger_retraining, do_nothing_task]
