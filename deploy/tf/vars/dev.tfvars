# terraform.tfvars
project_id         = "<Your Google Cloud Project ID>"
region             = "europe-west4" # Or your desired region
my_org             = "<your-org-domain.com>"
service_name       = "video-intelligence"
# artifact_repo_name = "video-intelligence" # Optional, defaults to service_name
# log_level          = "INFO" # Optional, defaults to INFO

# --- Settings for Access Control ---
# These now default to public access, but you can override if needed
# cloud_run_allow_unauthenticated = true
# cloud_run_ingress               = "all"
