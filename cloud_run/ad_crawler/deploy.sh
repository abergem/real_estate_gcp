export GRUN_REGION='europe-west1'
export GOOGLE_CLOUD_PROJECT='acn-dai-nordic'

gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/ad_crawler
gcloud beta run deploy ad_crawler --image gcr.io/$GOOGLE_CLOUD_PROJECT/ad_crawler --region $GRUN_REGION --platform managed

# gcloud functions deploy run_spider --runtime python37 \
#                                        --memory 1024MB \
#                                        --trigger-http \
#                                        --project $GOOGLE_CLOUD_PROJECT \
#                                        --region $GFUNC_REGION \
#                                        --timeout 540
#                                        #--env-vars-file env_vars.yaml \
                                       
