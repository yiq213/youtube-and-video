# Deployment

## Overview

### Terraform

- Terraform configuration is stored in `deploy/tf`.
- Override environment variables in the `dev.tfvars` and `prod.tfvars`.
- E.g. `terraform plan -var-file=vars/dev.tfvars`

### Cloud Run Application

 - The Cloud Run service is deployed/updated using Cloud Build, which is triggered by a push to the repo.
 - Cloud Build runs the build, based on the YAML, i.e. `deploy/cloudbuild.yaml`.
 - The YAML deploys the service using gcloud commands. (Terraform is not a sensible choice for deploying Cloud Run service revisions.)

## Steps

1. Create your Dev and Prod projects. Ensure you have required roles, or `Editor` role.
1. Proceed with the following steps using the `Dev` project.
1. Connect your GitHub repo to Cloud Build. See [Cloud Build Repository Setup](https://cloud.google.com/build/docs/repositories#whats_next). Name it `github-connection`.
1. Update your .env values.
1. Follow "Every Session" guidance from [../README.md](../README.md).
1. Enable APIs needed to run Terraform:

```bash
gcloud services enable \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```