#!/bin/sh

export GOOGLE_CLOUD_PROJECT='advance-nuance-248610'
export LANDING_BUCKET='advance-nuance-248610-realestate-ads-landing'
export GFUNC_REGION='europe-west1'

gcloud functions deploy transform \
    --runtime python37 \
    --trigger-resource $LANDING_BUCKET \
    --trigger-event google.storage.object.finalize \
    --project $GOOGLE_CLOUD_PROJECT \
    --region $GFUNC_REGION \
    --env-vars-file env_vars.yaml \
    --timeout 120
