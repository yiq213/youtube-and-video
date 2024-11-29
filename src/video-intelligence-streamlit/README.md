# Guidance for Running and Deploying the Video Intelligence Streamlit Application

```bash
export PROJECT_ID='<Your Google Cloud Project ID>'
export REGION='<your region>'
export LOG_LEVEL='DEBUG'
export VERSION="0.1"
export REPO=video-intelligence
export SERVICE_NAME=video-intelligence

# Enable APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com \
  storage-component.googleapis.com \
  aiplatform.googleapis.com

# Allow service account to access GCS Cloud Build bucket
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:608831385073-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"

# Setup Python environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To run and test the application locally:

```bash
# Local streamlit app
streamlit run app.py \
  --browser.serverAddress=localhost \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false

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

To upload to Google Artifact Registry:

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

To deploy to Cloud Run:

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
  ```