# Command to cretae cluster - doesn't allow for VPC native routing - can't see why we'd need
#  --enable-ip-alias Might be useful to give each pod its own IP not using unless we need it
gcloud container clusters create gameserver-cluster `
    --region=europe-west2-c