from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from libs.crypto_data_downloader_for_airflow import CryptoDataDownloader, MainApplicationForAirFlow  

def run_single_day(coin_id, date):
    app = MainApplicationForAirFlow(coin_id=coin_id, date=date)
    app.run()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_data_downloader',
    default_args=default_args,
    description='DAG for downloading cryptocurrency data',
    schedule_interval=timedelta(days=1),
    catchup=False,
)


download_task = PythonOperator(
    task_id='download_crypto_data',
    python_callable=run_single_day,
    op_kwargs={'coin_id': 'bitcoin', 'date': '{{ ds }}'},  
    dag=dag,
)

download_task
