locals {
  apis = [
    "cloudbuild.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "storage-component.googleapis.com", 
    "storage.googleapis.com", 
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "secretmanager.googleapis.com",
    "iap.googleapis.com"
  ]

  roles = [
    "roles/serviceusage.serviceUsageAdmin",
    "roles/iam.serviceAccountAdmin",
    "roles/aiplatform.user",
    "roles/storage.admin",
    "roles/cloudbuild.builds.builder",
    "roles/run.admin",
    "roles/run.invoker",
    "roles/storage.admin",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/artifactregistry.writer",
    "roles/secretmanager.secretAccessor",
    "roles/cloudbuild.connectionAdmin", 
    "roles/resourcemanager.projectIamAdmin",
    "roles/iap.admin"
  ]
}