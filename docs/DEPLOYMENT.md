# Deployment Guide for Discord Dr. Shamer Bot

## Prerequisites

1. **Google Cloud SDK installed** and authenticated
2. **Docker** installed and running
3. **Terraform** installed (version 1.0+)
4. **Discord Bot Token** ready

## Initial Setup

### 1. Google Cloud Project Setup

```bash
# Set your project ID
export PROJECT_ID="ldn-discord-dr-shamer"

# Create the project (if not already created)
gcloud projects create $PROJECT_ID

# Set as default project
gcloud config set project $PROJECT_ID

# Enable billing (required for Cloud Run)
# This must be done via the Google Cloud Console
```

### 2. Authentication Setup

```bash
# Authenticate with Google Cloud
gcloud auth login

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 3. Environment Variables

Create a `.env` file or set environment variables:
```bash
# Option 1: Create .env file
echo "DISCORD_BOT_TOKEN=your_discord_bot_token_here" > .env

# Option 2: Export directly
export DISCORD_BOT_TOKEN="your_discord_bot_token_here"
```

## Deployment Process

### 1. First-time Deployment (Staged Approach)

**Step 1: Deploy Basic Infrastructure**
```bash
# Deploy APIs and Artifact Registry (no secrets needed)
./deploy.sh
```

**Step 2: Build and Push Docker Image**
```bash
# Build and push Docker image (no secrets needed)
./build_docker.sh
```

**Step 3: Deploy the Bot**
```bash
# Deploy Cloud Run service (requires Discord token)
source .env && ./deploy.sh

# Alternative .env loading methods:
# set -a && source .env && set +a && ./deploy.sh
# env $(cat .env | xargs) ./deploy.sh
# export $(cat .env | xargs) && ./deploy.sh
```

### 2. Subsequent Deployments

```bash
# Build new version and deploy
./build_docker.sh
source .env && ./deploy.sh

# Or in one line:
./build_docker.sh && source .env && ./deploy.sh
```
