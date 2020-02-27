#!/bin/sh

export GOOGLE_CLOUD_PROJECT='advance-nuance-248610'
export BUCKET='advance-nuance-248610-realestate-ads'
export GFUNC_REGION='europe-west1'

gcloud functions deploy transform_ad_data \
    --runtime python37 \
    --trigger-resource $BUCKET \
    --trigger-event google.storage.object.finalize \
    --project $GOOGLE_CLOUD_PROJECT \
    --region $GFUNC_REGION \
    --env-vars-file env_vars.yaml \
    --timeout 120
