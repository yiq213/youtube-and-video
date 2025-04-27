# Set up the connection between the Google Cloud project 
# (specifically Cloud Build) and the GitHub repository

provider "github" {
  token = data.google_secret_manager_secret_version_access.github_token.secret_data
  owner = var.repository_owner
}

# Grant the Cloud Build Service Agent access to the specific secret
# Use the iam_member resource to actively manage the permission
# resource "google_secret_manager_secret_iam_member" "cloudbuild_secret_accessor" {
#   # Grant permission on the secret itself
#   project   = var.project_id
#   secret_id = var.github_pat_secret_id # Reference the secret name via variable
#   role      = "roles/secretmanager.secretAccessor"
#   member    = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"

#   depends_on = [
#     # Ensure the secret exists
#     data.google_secret_manager_secret_version_access.github_token,
#     resource.google_project_service.apis
#   ]
# }

# Fetch the GitHub PAT secret
data "google_secret_manager_secret_version_access" "github_token" {
  secret = var.github_pat_secret_id
  depends_on = [resource.google_project_service.apis]
}

# Create the GitHub connection
resource "google_cloudbuildv2_connection" "github_connection" {
  count      = var.connection_exists ? 0 : 1
  project    = var.project_id
  location   = var.cb_region
  name       = "github-connection"

  github_config {
    app_installation_id = var.github_app_installation_id
    authorizer_credential {
      oauth_token_secret_version = data.google_secret_manager_secret_version_access.github_token.id
    }
  }
  depends_on = [
    # google_secret_manager_secret_iam_member.cloudbuild_secret_accessor,
    resource.google_project_service.apis]
}

# Try to get existing repo
data "github_repository" "existing_repo" {
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# Link the GitHub repo to the Cloud Build connection
resource "google_cloudbuildv2_repository" "repo" {
  project  = var.project_id
  location = var.cb_region
  name     = var.repository_name
  
  parent_connection = one(google_cloudbuildv2_connection.github_connection[*].id)
  remote_uri       = "https://github.com/${var.repository_owner}/${var.repository_name}.git"
  depends_on = [
    resource.google_project_service.apis,
    data.github_repository.existing_repo
  ]
}
