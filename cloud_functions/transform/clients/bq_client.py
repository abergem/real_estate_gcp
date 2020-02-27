

class bqClient():
    def __init__(self):
        self.project = os.environ['GOOGLE_CLOUD_PROJECT']
        self.client = bigquery.Client()
        dataset_id = os.environ['DATASET_ID']
        dataset_ref = self.client.dataset(dataset_id)
        self.dataset = bigquery.Dataset(dataset_ref)
        self.dataset.location = "EU"
    
    def update_dataset(self):
        if True:
            dataset = self.client.create_dataset(self.dataset)
            print(f'Created dataset {self.client.project}.{dataset.dataset_id}')

    def populate_table(self, csv_path):
        table_id = 'cdf_all_kpis'
        table_ref = self.dataset.table(table_id)
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.JSON
        job_config.autodetect = True

        with open(csv_path, 'rb') as f:
            job = self.client.load_table_from_file(f, table_ref, job_config=job_config)
        
        job.result()
        print(f'Loaded {job.output_rows} rows into {self.dataset.dataset_id}:{table_id}')