terraform {
  backend "gcs" {
    bucket = "ldn-discord-dr-shamer-terraform-state"
    prefix = "terraform/state"
  }
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.0"
    }
  }
}

# Configure providers
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "cloud_run" {
  count   = var.discord_bot_token != "" ? 1 : 0
  project = var.project_id
  service = "run.googleapis.com"
}

resource "google_project_service" "container_registry" {
  project = var.project_id
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "artifact_registry" {
  project = var.project_id
  service = "artifactregistry.googleapis.com"
}

# Create Artifact Registry repository
resource "google_artifact_registry_repository" "discord_bot" {
  location      = var.region
  repository_id = "discord-bot"
  description   = "Docker repository for Discord Dr. Shamer bot"
  format        = "DOCKER"
  
  depends_on = [google_project_service.artifact_registry]
} 