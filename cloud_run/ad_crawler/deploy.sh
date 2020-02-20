export GRUN_REGION='europe-west1'
export GOOGLE_CLOUD_PROJECT='advance-nuance-248610'
export TAG='adcrawler-chrome'

gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/$TAG
gcloud run deploy adcrawler --image gcr.io/$GOOGLE_CLOUD_PROJECT/$TAG:latest --region $GRUN_REGION --platform managed --memory 1Gi

curl -d '{"url":"https://www.finn.no/realestate/homes/search.html?location=0.20061&page=2"}' -H "Content-Type: application/json" -X POST https://adcrawler-e2ofq27tbq-ew.a.run.app
