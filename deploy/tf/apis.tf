# Enable necessary Google Cloud APIs

resource "google_project_service" "cicd_services" {
  count              = length(local.cicd_services)
  project            = var.project_id
  service            = local.cicd_services[count.index]
  disable_on_destroy = false
}

resource "google_project_service" "project_services" {
  count              = length(local.cicd_services)
  project            = var.project_id
  service            = local.cicd_services[count.index]
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  project = var.project_id
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "logging" {
  project = var.project_id
  service = "logging.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage" {
  project = var.project_id
  service = "storage-component.googleapis.com" # Usually enabled by default, but good to ensure
  disable_on_destroy = false
}

resource "google_project_service" "aiplatform" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  project = var.project_id
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam" {
  project = var.project_id
  service = "iam.googleapis.com"
  disable_on_destroy = false
}
