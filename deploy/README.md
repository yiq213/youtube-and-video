# Deployment

## Cloud Run Application

 - The Cloud Run service is deployed/updated using Cloud Build, which is triggered by a push to the repo.
 - Cloud Build runs the build, based on the YAML, e.g. `deploy-to-dev.yaml`.
 - The YAML deploys the service using gcloud commands. (Terraform is not a sensible choice for deploying Cloud Run service revisions.)

 