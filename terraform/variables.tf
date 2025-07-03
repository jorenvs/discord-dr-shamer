variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "ldn-discord-dr-shamer"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "bot_version" {
  description = "Version of the Discord bot to deploy"
  type        = string
  default     = "v1.0.0"
}

variable "discord_bot_token" {
  description = "Discord bot token (optional - if not provided, Cloud Run won't be deployed)"
  type        = string
  sensitive   = true
  default     = ""
} 