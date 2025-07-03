# GitHub Actions Setup Guide

This guide explains how to set up automated deployment using GitHub Actions.

## 🔑 Required GitHub Secrets

You need to add these secrets to your GitHub repository:

### 1. Google Cloud Service Account Key (`GCP_SA_KEY`)

**Create a service account:**
```bash
# Create service account
gcloud iam service-accounts create discord-bot-deployer \
    --description="Service account for Discord bot deployment" \
    --display-name="Discord Bot Deployer"

# Get the email
SA_EMAIL="discord-bot-deployer@ldn-discord-dr-shamer.iam.gserviceaccount.com"

# Grant necessary permissions
gcloud projects add-iam-policy-binding ldn-discord-dr-shamer \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding ldn-discord-dr-shamer \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding ldn-discord-dr-shamer \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/serviceusage.serviceUsageAdmin"

gcloud projects add-iam-policy-binding ldn-discord-dr-shamer \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding ldn-discord-dr-shamer \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create discord-bot-key.json \
    --iam-account="${SA_EMAIL}"
```

**Add to GitHub:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GCP_SA_KEY`
4. Value: Copy the entire contents of `discord-bot-key.json`

### 2. Discord Bot Token (`DISCORD_BOT_TOKEN`)

**Add to GitHub:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DISCORD_BOT_TOKEN`
4. Value: Your Discord bot token (from Discord Developer Portal)

## 🗂️ Create Terraform State Bucket

**Create the GCS bucket for Terraform state:**
```bash
# Create bucket (one-time setup)
gsutil mb gs://ldn-discord-dr-shamer-terraform-state

# Enable versioning
gsutil versioning set on gs://ldn-discord-dr-shamer-terraform-state
```

**Bucket name**: `ldn-discord-dr-shamer-terraform-state`

## 🚀 How the Workflow Works

### **On Push to Main:**
- ✅ Generates semantic version from commit messages
- ✅ Builds Docker image
- ✅ Pushes image to Artifact Registry
- ✅ Deploys with Terraform
- ✅ Creates Git tag

### **Remote State Management**
- Terraform state is stored in Google Cloud Storage
- Enables team collaboration and persistent deployments
- **Prerequisite**: GCS bucket must exist (see setup below)

## 📋 Deployment Process

1. **Make changes** to `bot.py` or other files
2. **Use conventional commits** to indicate version bump type
3. **Push to main** → GitHub Actions builds, deploys, and tags automatically
4. **Bot is live** with new semantic version!

## 🔧 Manual Override

If you need to deploy manually, use the archived scripts:
```bash
# Use archived legacy scripts if needed
./archive/build_docker.sh
source .env && ./archive/deploy.sh
```

## 🎯 Version Management

### Semantic Versioning with Conventional Commits

The bot uses **semantic versioning** based on your commit messages:

**Commit Message Format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Version Bumping:**
- **Patch** (`v1.0.0` → `v1.0.1`): Any commit
- **Minor** (`v1.0.0` → `v1.1.0`): Commits starting with `feat:`
- **Major** (`v1.0.0` → `v2.0.0`): Commits containing `BREAKING CHANGE:`

**Examples:**
```bash
# Patch version (bug fixes)
git commit -m "fix: resolve wish detection issue"

# Minor version (new features)
git commit -m "feat: add new shame messages"

# Major version (breaking changes)
git commit -m "feat: redesign bot architecture

BREAKING CHANGE: config format changed"
```

**Commit Types:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions
- `chore:` - Maintenance tasks 