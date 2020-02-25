'''
Scheduler to run crawler trigger
Every day at noon
'''

import os
import json
from google.api_core.exceptions import NotFound
from google.cloud import scheduler_v1

# Create non-empty data to be passed to pub/sub msg
data = {}
data = json.dumps(data).encode('utf-8')

# Instantiate scheduler client
client = scheduler_v1.CloudSchedulerClient()

# Get env vars and create job/topic strings
project_name = os.getenv('GOOGLE_CLOUD_PROJECT')
appengine_location = os.getenv('APPENG_LOCATION')
job_id = 'pronova_cntx_cronjob'
topic_id = os.getenv('TOPIC_NAME_CNTX')
job_name = f'projects/{project_name}/locations/{appengine_location}/jobs/{job_id}'
topic_name = f'projects/{project_name}/topics/{topic_id}'

parent = client.location_path(project_name, appengine_location)
job = {
    'name': job_name,
    'pubsub_target': {'topic_name': topic_name,
                      'data': data},
    'schedule': '0 12 * * *',
    'time_zone': 'Europe/Oslo'
}

# If cronjob exists, update it, if not, create it
try:
    client.get_job(job_name)
    update_mask = {'paths': list(job.keys())}
    client.update_job(job, update_mask)
    print('Cronjob updated')
except NotFound as e:
    client.create_job(parent, job)
    print('Cronjob created')
