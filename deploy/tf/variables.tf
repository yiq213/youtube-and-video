# Input variables for the Terraform configuration

variable "project_id" {
  description = "The Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "The Google Cloud region for deployment."
  type        = string
  default     = "europe-west4" # Or your preferred default
}

variable "my_org" {
  description = "Your organization's domain (e.g., example.com)."
  type        = string
}

variable "devops_group_email" {
  description = "The email address of the DevOps group for IAM permissions."
  type        = string
  # Example: "gcp-devops@your-org.com"
}

variable "service_name" {
  description = "The name for the Cloud Run service and related resources."
  type        = string
  default     = "video-intelligence"
}

variable "artifact_repo_name" {
  description = "The name for the Artifact Registry repository."
  type        = string
  default     = "video-intelligence" # Matches the service name by default
}

variable "log_level" {
  description = "Log level environment variable for the Cloud Run service."
  type        = string
  default     = "INFO"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of instances for the Cloud Run service."
  type        = number
  default     = 1
}

variable "cloud_run_allow_unauthenticated" {
  description = "Allow unauthenticated access to the Cloud Run service."
  type        = bool
  default     = true # Defaulting to true for public access scenario
}

variable "cloud_run_ingress" {
  description = "Ingress setting for Cloud Run ('all', 'internal-only', 'internal-and-cloud-load-balancing')."
  type        = string
  default     = "all" # Defaulting to 'all' for public access scenario
  validation {
    condition     = contains(["all", "internal-only", "internal-and-cloud-load-balancing"], var.cloud_run_ingress)
    error_message = "Allowed values for cloud_run_ingress are: all, internal-only, internal-and-cloud-load-balancing."
  }
}

variable "cicd_roles" {
  description = "List of roles to assign to the CICD runner service account"
  type        = list(string)
  default = [
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin",
    "roles/cloudbuild.builds.builder",
    "roles/run.admin"
    "roles/run.invoker",
    "roles/storage.admin",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/artifactregistry.writer"    
  ]
}