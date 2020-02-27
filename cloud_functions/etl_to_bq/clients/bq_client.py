import os
from google.cloud import bigquery

class bqClient():
    def __init__(self):
        self.project = os.environ['GOOGLE_CLOUD_PROJECT']
        self.client = bigquery.Client()
        dataset_id = os.environ['DATASET_ID']
        dataset_ref = self.client.dataset(dataset_id)
        self.dataset = bigquery.Dataset(dataset_ref)
        self.dataset.location = os.environ['DATASET_LOCATION']
        self.schema = [
            bigquery.SchemaField("finn_code", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("address", "STRING", mode="REQUIRED"),
            
            bigquery.SchemaField("price", "NUMERIC", mode="REQUIRED"),
            bigquery.SchemaField("fees", "NUMERIC", mode="NULLABLE"),
            bigquery.SchemaField("total_price", "NUMERIC", mode="NULLABLE"),
            bigquery.SchemaField("overheads", "NUMERIC", mode="NULLABLE"),

            bigquery.SchemaField("joint_debt", "NUMERIC", mode="NULLABLE"),
            bigquery.SchemaField("joint_capital", "NUMERIC", mode="NULLABLE"),
            bigquery.SchemaField("asset_value", "NUMERIC", mode="NULLABLE"),
            
            bigquery.SchemaField("type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("tenure", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("floor", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("year_of_construction", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("energy_class", "STRING", mode="NULLABLE"),

            bigquery.SchemaField("lot_space", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("gross_floor_space", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("rooms", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("bedrooms", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("net_internal_area", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("gross_internal_area", "INT64", mode="NULLABLE"),
            
            bigquery.SchemaField("longitude", "NUMERIC", mode="NULLABLE"),
            bigquery.SchemaField("latitude", "NUMERIC", mode="NULLABLE"),
            bigquery.SchemaField("geo_area", "STRING", mode="NULLABLE"),

            bigquery.SchemaField("last_edited", "DATETIME", mode="NULLABLE"),
            
        ]

    def load_file_to_table(self, local_file_path):
        table_id = os.environ['TABLE_ID']
        table_ref = self.dataset.table(table_id)

        # Job config
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.schema = self.schema

        with open(local_file_path, 'rb') as f:
            job = self.client.load_table_from_file(f, table_ref, job_config=job_config)
        
        job.result()
        print(f'Loaded {job.output_rows} rows into {self.dataset.dataset_id}:{table_id}')

'''
To view bq jobs run these CLI commands:
bq ls -j -a advance-nuance-248610   -> you'll get the job_id
bq show -j job_id
'''

