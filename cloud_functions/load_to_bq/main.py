"""Import a json file into BigQuery."""

import os
import json
from google.cloud import storage
from clients.bq_client import bqClient
from datetime import datetime

GCP_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')


def load_to_bq(data, context):
    # Triggered by cloud scheduler
    
    storage_client = storage.Client()
    bucket_name = os.environ['PROCESSED_FILES_BUCKET']
    bucket = storage_client.bucket(bucket_name)

    # Iterate over all json files in bucket
    year, month, day = datetime.today().year, datetime.today().month, datetime.today().day
    date_tag = str(year)+str(month)+str(day)
    blobs = storage_client.list_blobs(bucket_name, delimiter='/', prefix=f'processed/{date_tag}/')
    
    # Merge all json files
    l = []
    for blob in blobs:
        blob_string = blob.download_as_string()
        d = json.loads(blob_string)
        l.append(d)
    result = [json.dumps(record) for record in l]
    #json_newline_delimited = '\n'.join(result) 

    # Download json delimited file to local tmp folder
    file_name = 'merged_ndjson'
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    merged_file_path = os.path.join('/tmp', file_name)
    with open(merged_file_path, 'w') as obj:
        for i in result:
            obj.write(i+'\n')

    # Load merged file to bigquery
    bq_client = bqClient()
    bq_client.load_file_to_table(merged_file_path)
    


if __name__ == '__main__':
    from export_env_vars import export_env_vars
    export_env_vars()

    load_to_bq(None, None)