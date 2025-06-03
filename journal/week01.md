# Week 1
## Terraform
I'll be learning Terraform during this process for IaC. The code will be located in `aws/terraform/`. Initial setup is storing the Terraform state in an S3 bucket using DynamoDB as a locking mechanism.
## Auth Microservice
### dev DB
- Set up docker compose to create a postgres image for the auth microservice.
- Helper scripts located in `bin/auth_db/`
### Installs for auth service
```sh
python3 -m venv venv
source venv/bin/activate
pip install pyjwt
pip install flask
pip install psycopg2-binary
deactivate
```
## Kubernetes
The auth service's Kubernets configs are located in `python/src/auth/manifests`.
They're currently set to pull CONNECTION_URL and JWT_SECRET from AWS SSM Paramter Store.
### Generate ECR credentials secret
We'll be needing to install go and helm for this process.
After, to be able to use external secrets:
```sh
kubectl apply -f https://raw.githubusercontent.com/external-secrets/external-secrets/main/deploy/crds/bundle.yaml
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace \
  --set installCRDs=false
```
To store ECR credentials to be able to pull image from ECR:
```sh
kubectl create secret docker-registry ecr-creds \
  --docker-server=009160064216.dkr.ecr.us-west-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password="$(aws ecr get-login-password --region us-west-1)"
```
In `python/src/auth/manifests/`:
```sh
kubectl apply -f ./
```