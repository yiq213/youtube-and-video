# Define the Cloud Run service

resource "google_cloud_run_v2_service" "main" {
  project  = var.project_id
  location = var.region
  name     = var.service_name

  # Set ingress based on variable (defaults to 'all' for public access)
  ingress = var.cloud_run_ingress

  template {
    scaling {
      max_instance_count = var.cloud_run_max_instances
    }

    containers {
      # IMPORTANT: Set an initial image. Your CI/CD pipeline (Cloud Build)
      # will update this image URL using 'gcloud run deploy'.
      # The lifecycle block below tells Terraform to ignore external changes to the image.
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/${var.service_name}:initial" # Placeholder/initial image

      ports {
        container_port = 8080 # Port your container listens on
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }
      # Add other necessary environment variables here
    }

    # Enable CPU boost if specified
    execution_environment = var.cloud_run_cpu_boost ? "EXECUTION_ENVIRONMENT_GEN2" : "EXECUTION_ENVIRONMENT_DEFAULT" # Assuming Gen2 for boost
  }

  lifecycle {
    # Tell Terraform to ignore changes to the image URL made outside of Terraform (e.g., by Cloud Build)
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  depends_on = [
    google_project_service.run,
    google_artifact_registry_repository.repo, # Ensure repo exists before service referencing its potential images
  ]
}

# Output the URL of the Cloud Run service
output "cloud_run_service_url" {
  description = "URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.main.uri
}
