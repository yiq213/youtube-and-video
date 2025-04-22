terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "< 7.0.0"
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
