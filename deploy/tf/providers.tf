terraform {
  required_version = ">= 1.9.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "< 7.0.0" # Use latest version that satisfies this condition
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
