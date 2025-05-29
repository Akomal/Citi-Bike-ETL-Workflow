from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.gcs import GCSDeleteObjectsOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

# Custom Python callables
from citi_bike_scrapper import fetch_and_upload
from validation_bronze import validate_latest_file
from silver_transformation import raw_transformation
from silver_data_quality import validate_parquet_file

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2
}

with DAG(
    dag_id='citi_bike_bronze_ingestion',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    template_searchpath='/home/airflow/gcs/data/',
    tags=['citi_bike'],
    params={
        "bronze_bucket": "bronze113",
        "silver_bucket": "silver113"
    }
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_to_bronze',
        python_callable=fetch_and_upload,
        op_kwargs={"bucket_name": "{{ params.bronze_bucket }}"},
    )

    validate_task = PythonOperator(
        task_id='validate_bronze',
        python_callable=validate_latest_file,
    )

    transform_task = PythonOperator(
        task_id='transform_to_silver',
        python_callable=raw_transformation,
        op_kwargs={"bucket_name": "{{ params.silver_bucket }}"},
    )

    dq_silver_validation = PythonOperator(
    task_id='validate_silver_data_quality',
    python_callable=validate_parquet_file,
)


    load_parquet_to_bq = GCSToBigQueryOperator(
        task_id='load_silver_parquet_to_bigquery',
        bucket='silver113',
        source_objects=['citi-bike/*.parquet'],
        destination_project_dataset_table='citi-bike-459310.lake_silver.master_bike_station_status',
        source_format='PARQUET',
        write_disposition='WRITE_APPEND',
        autodetect=True,
        project_id='citi-bike-459310',
    )

    clear_silver_task = GCSDeleteObjectsOperator(
        task_id='clear_silver_folder',
        bucket_name='silver113',
        prefix='citi-bike/',
    )

    populate_gold_table = BigQueryInsertJobOperator(
        task_id='populate_gold_station_utilization_weekly',
        configuration={
            "query": {
                "query": "{% include 'populate_gold_station_utilization_weekly.sql' %}",
                "useLegacySql": False
            }
        },
    )

    # DAG dependencies
    ingest_task >> validate_task >> transform_task >> dq_silver_validation >> load_parquet_to_bq >> clear_silver_task >> populate_gold_table
