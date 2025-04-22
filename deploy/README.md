# Deployment

## Terraform

- Terraform configuration is stored in `deploy/tf`.
- Override environment variables in the `dev.tfvars` and `prod.tfvars`.
- E.g. `terraform plan -var-file=vars/dev.tfvars`

## Cloud Run Application

 - The Cloud Run service is deployed/updated using Cloud Build, which is triggered by a push to the repo.
 - Cloud Build runs the build, based on the YAML, i.e. `deploy/cloudbuild.yaml`.
 - The YAML deploys the service using gcloud commands. (Terraform is not a sensible choice for deploying Cloud Run service revisions.)

 