"""Import a json file into BigQuery."""

import os
import json
from google.cloud import storage
import googlemaps
from clients.bq_client import bqClient
from datetime import datetime

GCP_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')


def transform_ad_data(data, context):
    ''' Example of payload:
    "{'bucket': 'advance-nuance-248610-realestate-ads', 'contentType': 'application/json', 'crc32c': 'dTWIWg==', 
    'etag': 'CICX7e2H8OcCEAE=', 'generation': '1582749097610112', 'id': 'advance-nuance-248610-realestate-ads/landing/171235821.json/1582749097610112', 
    'kind': 'storage#object', 'md5Hash': '+u9ZU+DfgZdaKgcwEbWjxg==', 
    'mediaLink': 'https://www.googleapis.com/download/storage/v1/b/advance-nuance-248610-realestate-ads/o/landing%2F171235821.json?generation=1582749097610112&alt=media', 
    'metageneration': '1', 
    'name': 'landing/171235821.json', 
    'selfLink': 'https://www.googleapis.com/storage/v1/b/advance-nuance-248610-realestate-ads/o/landing%2F171235821.json', 
    'size': '480', 'storageClass': 'STANDARD', 'timeCreated': '2020-02-26T20:31:37.609Z', 'timeStorageClassUpdated': '2020-02-26T20:31:37.609Z', 
    'updated': '2020-02-26T20:31:37.609Z'}"
    '''
    
    print(data)

    # Get blob metadata
    bucket_name = data['bucket']
    source_file_path = data['name']

    # Download blob to local file in tmp folder
    file_name = source_file_path.split('/')[1]
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_file_path)
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    destination_path = os.path.join('tmp', file_name)
    blob.download_to_filename(destination_path)

    # Load json 
    with open(destination_path) as json_file:
        data = json.load(json_file)

    # Cast last_edited from string to datetime
    data['last_edited'] = datetime.strptime(data['last_edited'], '%d/%m/%Y %H:%M')

    # Get geo data from googlemaps API
    api_key_blob = bucket.blob('secrets/api-key.txt')
    api_key = api_key_blob.download_as_string()
    api_key = api_key.decode()
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(data['address'])
    data['geo_area'] = geocode_result[0]['address_components'][2]['short_name']
    data['longitude'] = geocode_result[0]['geometry']['location']['lng']
    data['latitude'] = geocode_result[0]['geometry']['location']['lat']

    # Save processed json file to local tmp folder
    processed_file_name = 'processed_' + file_name
    processed_file_path = os.path.join('tmp', processed_file_name)
    with open(processed_file_path, 'w') as outfile:
        json.dump(data, outfile, default=json_converter)

    # Upload processed file to cloud storage
    # destination_blob_path = os.path.join('processed', processed_file_name)
    # blob = bucket.blob(destination_blob_path)
    # blob.upload_from_filename(processed_file_path)
    # print(f'Processed and uploaded file: {file_name}')

    # Load processed file to bigquery
    bq_client = bqClient()
    bq_client.load_file_to_table(processed_file_path)

def json_converter(o):
    # from: https://code-maven.com/serialize-datetime-object-as-json-in-python
    if isinstance(o, datetime):
        return o.__str__()
    


if __name__ == '__main__':
    from export_env_vars import export_env_vars
    export_env_vars()

    data = {}
    data['bucket'] = 'advance-nuance-248610-realestate-ads'
    data['name'] = 'landing/171366624.json'
    transform_ad_data(data, None)