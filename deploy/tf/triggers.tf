resource "google_cloudbuild_trigger" "cd_pipeline" {
  project = var.project_id
  location = var.region
  name    = "deploy-video-intelligence"
  service_account = resource.google_service_account.cicd_runner_sa.id
  description = "Trigger for ${var.trigger_branch_name} branch deployment"

  repository_event_config {
    repository = google_cloudbuildv2_repository.repo.id
    push {
      branch = "^${var.trigger_branch_name}$"
    }
  }

  filename = "deploy/cloudbuild.yaml"
  included_files = [
    "src/**",
    "tests/**",
    "deploy/**"
  ]

  ignored_files   = ["README.md"] # Add this line to ignore README.md changes

  # Define substitutions - these override defaults in cloudbuild.yaml
  substitutions = {
    _DEPLOY_REGION                 = var.region
    _AR_HOSTNAME                   = "${var.region}-docker.pkg.dev"
    _PLATFORM                      = "managed"
    _SERVICE_NAME                  = var.service_name
    _LOG_LEVEL                     = "DEBUG"
    _MAX_INSTANCES                 = "1"
  }

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.project_services, google_cloudbuildv2_repository.repo]

  tags = [
    "terraform-managed",
    var.service_name, # Match tags in your cloudbuild.yaml if desired
    var.trigger_branch_name # Tag with the branch/environment
  ]

  lifecycle {
    # Prevent accidental deletion if the trigger is manually modified
    prevent_destroy = false # Set to true in production if desired
  }
}