# Create Artifact Registry repository for Docker images

resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_repo_name
  description   = "Image repository application"
  format        = "DOCKER"

  depends_on = [resource.google_project_service.apis] # Ensure APIs enabled
}
