# Supply the backend bucket name dynamically when we run terraform
# E.g. terraform init -backend-config="bucket={PROJECT_ID}-tfstate"
terraform {
  backend "gcs" {
    prefix = "terraform/state"
  }
}
