# Set up the connection between the Google Cloud project (specifically Cloud Build) 
# and the GitHub repository

provider "github" {
  token = data.google_secret_manager_secret_version.github_token.secret_data
  owner = var.repository_owner
}

# Fetch the GitHub PAT secret
data "google_secret_manager_secret_version" "github_token" {
  project = var.project_id
  secret  = var.github_pat_secret_id
  version = "latest"
}

# Create the GitHub connection
resource "google_cloudbuildv2_connection" "github_connection" {
  count      = var.connection_exists ? 0 : 1
  project    = var.project_id
  location   = var.region
  name       = "github-connection"

  github_config {
    app_installation_id = var.github_app_installation_id
    authorizer_credential {
      oauth_token_secret_version = "projects/${var.project_id}/secrets/${var.github_pat_secret_id}/versions/latest"
    }
  }
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.project_services]
}

# Try to get existing repo
data "github_repository" "existing_repo" {
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# Link the GitHub repo to the Cloud Build connection
resource "google_cloudbuildv2_repository" "repo" {
  project  = var.project_id
  location = var.region
  name     = var.repository_name
  
  parent_connection = "projects/${var.project_id}/locations/${var.region}/connections/github-connection"
  remote_uri       = "https://github.com/${var.repository_owner}/${var.repository_name}.git"
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.shared_services,
    data.github_repository.existing_repo
  ]
}
