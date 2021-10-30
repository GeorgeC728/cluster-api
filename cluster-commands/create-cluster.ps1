# Command to create cluster - one for everything atm
gcloud container clusters create main-cluster `
    --region=europe-west2-c `
    --enable-ip-alias `
    --num-nodes=1 `
    --machine-type=e2-standard-4 `
    --preemptible `
    --disk-size=20 `
    --tags=gameservers