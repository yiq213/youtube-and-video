# Guidance for Running and Deploying the Video Intelligence Streamlit Application

## Every Session

For local dev, always set these variables:

```bash
# Set these manually...
export PROJECT_ID='<Your Google Cloud Project ID>'
export REGION='<your region>'

# Or load from .env
source ../../.env

export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

export LOG_LEVEL='DEBUG'
export VERSION="0.1"
export REPO=video-intelligence
export SERVICE_NAME=video-intelligence
export CLOUD_RUN_INVOKER_SA="video-intelligence-invoker-sa"
export CLOUD_RUN_INVOKER_SA_EMAIL="$CLOUD_RUN_INVOKER_SA@$PROJECT_ID.iam.gserviceaccount.com"

# Check we're in the correct project
gcloud config list project
gcloud config set project $PROJECT_ID

gcloud auth login # authenticate yourself to gcloud

# setup ADC so any locally running application can access Google APIs
# Note that credentials will be saved to ~/.config/gcloud/application_default_credentials.json
gcloud auth application-default login
```

## One-Time Google Cloud Setup

```bash
# Enable APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com \
  storage-component.googleapis.com \
  aiplatform.googleapis.com

# Allow service account to access GCS Cloud Build bucket
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"
```

## Running and Testing the Application Locally

### Per-Environment Setup

```
# Setup Python environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Streamlit App

```bash
# Local streamlit app
streamlit run app.py --browser.serverAddress=localhost
```

### Running in a Local Container

```bash
# To build as a container image
docker build -t $SERVICE_NAME:$VERSION .

# To run as a local container
# We need to pass environment variables to the container
# and the Google Application Default Credentials (ADC)
docker run --rm -p 8080:8080 \
  -e PROJECT_ID=$PROJECT_ID -e REGION=$REGION \
  -e LOG_LEVEL=$LOG_LEVEL \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/.config/gcloud/application_default_credentials.json" \
  --mount type=bind,source=${HOME}/.config/gcloud,target=/app/.config/gcloud \
   $SERVICE_NAME:$VERSION
```

## Running in Google Cloud

### Build and Push to Google Artifact Registry:

```bash
# Create a GAR repo
gcloud artifacts repositories create "$REPO" \
  --location="$REGION" --repository-format=Docker

# Allow authentication to the repo
gcloud auth configure-docker "$REGION-docker.pkg.dev"

# Build to GAR - this takes a few minutes
gcloud builds submit \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION"
```

### Deploy to Cloud Run

Public service with no authentication:

```bash
# Deploy to Cloud Run - this takes a couple of minutes
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME" \
  --allow-unauthenticated \
  --region=$REGION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=DEBUG

  APP_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format="value(status.address.url)")
  ```

This time, the service will require authentication. It will require a service account that is authorised.

```bash
# Delete the existing service
gcloud run services delete $SERVICE_NAME --region $REGION

# Create the SA
gcloud iam service-accounts create $CLOUD_RUN_INVOKER_SA

# Deploy to Cloud Run - this takes a couple of minutes
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME" \
  --no-allow-unauthenticated \
  --region=$REGION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=DEBUG

  APP_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format="value(status.address.url)")

# Assign the Invoker Service SA as a principal on the target service,
# i.e. the Cloud Run service
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --member=serviceAccount:$CLOUD_RUN_INVOKER_SA@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.invoker \
  --region $REGION \
  --platform managed
  ```