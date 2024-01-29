from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.sql_sensor import SqlSensor
from airflow.models import Variable
from libs.crypto_data_downloader_for_airflow import MainApplicationForAirFlow
from libs.crypto_analysis import CryptoAnalysis 

def run_30_days(coin_id, start, end):
    api_key = "CG-FzSij3qa7YXK18Kzfsn6xA3v" 
    app = MainApplicationForAirFlow(coin_id=coin_id, start_date=start ,end_date=end, db=True)
    app.run(apikey=api_key)

def plot_and_calculate(coin_id, **context):
    analyst = CryptoAnalysis(coin_id)
    analyst.plot_prices(days=30)
    analyst.calculate_average_difference(days=30)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'daily_data_downloader_and_plotter',
    default_args=default_args,
    description='DAG for downloading cryptocurrency data and plotting prices',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

wait_for_data = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_stock_conn',
    sql=f"SELECT COUNT(*) FROM coin_data WHERE coin='bitcoin' AND date='{datetime.now().date()}'",
    dag=dag,
)

download_task = PythonOperator(
    task_id='download_crypto_data',
    python_callable=run_30_days,
    op_kwargs={'coin_id': 'bitcoin', 'start': '{{ macros.ds_add(ds, -30) }}', 'end': '{{ ds }}' },
    dag=dag,
)

plot_and_calculate_task = PythonOperator(
    task_id='plot_and_calculate',
    python_callable=plot_and_calculate,
    op_kwargs={'coin_id': 'bitcoin'},  
    provide_context=True,
    dag=dag, 
)

download_task >> wait_for_data >> plot_and_calculate_task
