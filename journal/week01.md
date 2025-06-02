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