import pandas as pd
from sklearn.datasets import fetch_california_housing
from evidently.report import Report
from evidently.metrics import DataDriftTable, RegressionQualityMetric
import os
import mlflow
from datetime import datetime
import boto3

def generate_report():
    # Configure MLflow and MinIO
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv('MLFLOW_S3_ENDPOINT_URL', 'http://minio:9000')
    
    # Load data
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame
    
    # Prepare current data
    current_data = df.copy()
    
    # Load reference data from MLflow
    mlflow.set_tracking_uri("http://mlflow-server:5000")
    client = mlflow.tracking.MlflowClient()
    
    try:
        # Get latest model run
        runs = client.search_runs(
            experiment_ids=["0"],
            filter_string="tags.mlflow.runName = 'california_housing'",
            order_by=["attributes.start_time DESC"],
            max_results=1
        )
        
        if runs:
            run_id = runs[0].info.run_id
            ref_data_path = f"runs:/{run_id}/train_data.csv"
            reference_data = mlflow.artifacts.load_df(ref_data_path)
        else:
            reference_data = current_data.copy()
    except:
        reference_data = current_data.copy()

    # Prepare data with required columns
    current_data['target'] = current_data['MedHouseVal']
    current_data['prediction'] = current_data['MedHouseVal']  # Using same values for demo
    
    # Generate report with only DataDriftTable for now
    report = Report(metrics=[DataDriftTable()])
    report.run(reference_data=reference_data, current_data=current_data)
    
    # Save report locally and upload to MinIO
    report_date = datetime.now().strftime('%Y-%m-%d')
    local_path = f"/tmp/{report_date}_evidently_report.html"
    report.save_html(local_path)
    
    # Upload to MinIO
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('MLFLOW_S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD')
    )
    
    try:
        s3.upload_file(
            local_path,
            'reports',
            f"{report_date}_evidently_report.html",
            ExtraArgs={'ACL': 'public-read'}
        )
        print(f"Report successfully uploaded to s3://reports/{report_date}_evidently_report.html")
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        raise

if __name__ == "__main__":
    generate_report()
