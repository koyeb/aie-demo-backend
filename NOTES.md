# gCloud auth

Create a service account:

    gcloud iam service-accounts create aie-photoboot-demo --description "Account for the AIE photoboot demo to access the associated gcs bucket"

Give it access to the bucket (done via console).

Create a keyfile:

    gcloud iam service-accounts keys create keyfile.json --iam-account aie-photoboot-demo@prod-d1337e0f.iam.gserviceaccount.com

Use the keyfile, specifying its path with the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
