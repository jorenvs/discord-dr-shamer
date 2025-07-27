# Cloud Run service for Discord bot (only deploy if token is provided)
resource "google_cloud_run_service" "discord_bot" {
  count    = var.discord_bot_token != "" ? 1 : 0
  name     = "discord-dr-shamer"
  location = var.region
  
  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/discord-bot/dr-shamer:${var.bot_version}"
        
        # Discord bots need to run continuously
        resources {
          limits = {
            cpu    = "0.5"
            memory = "256Mi"
          }
        }
        
        env {
          name  = "DISCORD_BOT_TOKEN"
          value = var.discord_bot_token
        }
      }
      
      # Ensure the service stays running
      container_concurrency = 1
      timeout_seconds       = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "1"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_project_service.cloud_run,
    google_project_service.firestore,
    google_artifact_registry_repository.discord_bot
  ]
}

# IAM policy to allow the service to run
resource "google_cloud_run_service_iam_policy" "discord_bot" {
  count    = var.discord_bot_token != "" ? 1 : 0
  location = google_cloud_run_service.discord_bot[0].location
  project  = google_cloud_run_service.discord_bot[0].project
  service  = google_cloud_run_service.discord_bot[0].name

  policy_data = data.google_iam_policy.noauth[0].policy_data
}

data "google_iam_policy" "noauth" {
  count = var.discord_bot_token != "" ? 1 : 0
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
} 