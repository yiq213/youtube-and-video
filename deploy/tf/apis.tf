# Enable necessary Google Cloud APIs

resource "google_project_service" "apis" {
  count              = length(local.apis)
  project            = var.project_id
  service            = local.apis[count.index]
  disable_on_destroy = false
}
