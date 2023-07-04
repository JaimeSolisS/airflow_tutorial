from airflow import DAG
from datetime import datetime,timedelta

default_args = {
    "owner": "airflow", 
    "email_on_failure": False,
    "email_on_retry": False, 
    "email": "admin@localhost.com", 
    "retries": 1, 
    "retry_delay": timedelta(minutes=5)
}

with DAG(dag_id="forex_data_pipeline",
        start_date=datetime.datetime(2023, 1, 1),
        schedule_interval="@daily", 
        default_args=default_args, 
        catchup=False) as dag: