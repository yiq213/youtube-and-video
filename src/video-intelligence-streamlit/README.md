# Guidance for Running and Deploying the Video Intelligence Streamlit Application

## Every Session

For local dev, always set these variables:

```bash
gcloud auth login # authenticate yourself to gcloud

# setup ADC so any locally running application can access Google APIs
# Note that credentials will be saved to ~/.config/gcloud/application_default_credentials.json
gcloud auth application-default login

# Set these manually...
export PROJECT_ID='<Your Google Cloud Project ID>'
export REGION='<your region>'

export MY_ORG=<enter your org domain>
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Or load from .env
source ../../.env

export LOG_LEVEL='DEBUG'
export VERSION="0.1"
export REPO=video-intelligence
export SERVICE_NAME=video-intelligence

# Check we're in the correct project
gcloud config list project
gcloud config set project $PROJECT_ID
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

# Allow Compute Engine default service account to build with Cloud Build
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role="roles/cloudbuild.builds.builder"

# Allow Compute Engine default service account to access GCS Cloud Build bucket
# Not needed if we use roles/cloudbuild.builds.builder
# gcloud projects add-iam-policy-binding $PROJECT_ID \
#   --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
#   --role="roles/storage.admin"

# Grant the required role to the principal
# that will attach the service account to other resources.
# Here we assume your developer account is a member of the gcp-devops group.
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="group:gcp-devops@$MY_ORG" \
  --role="roles/iam.serviceAccountUser"

# Allow service account impersonation
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="group:gcp-devops@$MY_ORG" \
  --role=roles/iam.serviceAccountTokenCreator

gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member="group:gcp-devops@$MY_ORG" \
   --role roles/cloudfunctions.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member="group:gcp-devops@$MY_ORG" \
   --role roles/run.admin  

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="group:gcp-devops@$MY_ORG" \
  --role="roles/iap.admin"
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

# Build the image and push to the GAR - this takes a few minutes
gcloud builds submit \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION"
```

### Deploy to Cloud Run

Public service with no authentication:

```bash
# Deploy to Cloud Run - this takes a couple of minutes
# Set max-instances to 1 to minimise cost
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION" \
  --max-instances=1 \
  --allow-unauthenticated \
  --region=$REGION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=$LOG_LEVEL

APP_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format="value(status.address.url)")
echo $APP_URL
```

This time, the service will require authentication. It will require a service account that is authorised.

```bash
# Deploy to Cloud Run - this takes a couple of minutes
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION" \
  --max-instances=1 \
  --no-allow-unauthenticated \
  --region=$REGION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=DEBUG

APP_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format="value(status.address.url)")

### Setup IAP Access

```bash
export IAP_SA="service-$PROJECT_NUMBER@gcp-sa-iap.iam.gserviceaccount.com"

# Enable the IAP API
gcloud services enable iap.googleapis.com

# Create the required IAP service account
gcloud beta services identity create --service=iap.googleapis.com --project=$PROJECT_ID

# Grant the invoker permission to the service account
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --member="serviceAccount:$IAP_SA"  \
  --region=$REGION \
  --role="roles/run.invoker"
```

### Create the External Application Load Balancer

```bash
export DOMAIN_NAME="<enter domain>"
export SVC_LB_IP="lb-ip"
export SVC_CERT="svc-cert"
export SERVERLESS_NEG="$SERVICE_NAME-serverless-neg"
export BACKEND_SERVICE="$SERVICE_NAME-backend-service"
export URL_MAP="lb-url-map"
export TARGET_HTTP_PROXY="lb-target-proxy"
export FORWARDING_RULE="lb-forwarding-rule"

# Create global static external IP address
gcloud compute addresses create $SVC_LB_IP \
    --network-tier=PREMIUM \
    --ip-version=IPV4 \
    --global

# Check it and get IP
# We'll create a DNS A record pointing to this IP address later
gcloud compute addresses describe $SVC_LB_IP \
    --format="get(address)" \
    --global

# Create a managed SSL certificate
gcloud compute ssl-certificates create $SVC_CERT \
    --description="video-intel-alb-cert" \
    --domains=$DOMAIN_NAME \
    --global

# Check the status of the certificate
gcloud compute ssl-certificates list --global

# Create a serverless NEG for the serverless Cloud Run service
gcloud compute network-endpoint-groups create $SERVERLESS_NEG \
    --region=$REGION \
    --network-endpoint-type=serverless  \
    --cloud-run-service=$SERVICE_NAME

# Create ALB backend service
gcloud compute backend-services create $BACKEND_SERVICE \
    --load-balancing-scheme=EXTERNAL \
    --global

# Add the serverless NEG as a backend service
gcloud compute backend-services add-backend $BACKEND_SERVICE \
    --global \
    --network-endpoint-group=$SERVERLESS_NEG \
    --network-endpoint-group-region=$REGION

# Create URL map to route incoming requests to the backend service
gcloud compute url-maps create $URL_MAP \
    --default-service $BACKEND_SERVICE

# Create a target HTTPS proxy to route requests to your URL map
gcloud compute target-https-proxies create $TARGET_HTTP_PROXY \
    --ssl-certificates=$SVC_CERT \
    --url-map=$URL_MAP

# Create a forwarding rule to route incoming requests to the proxy
gcloud compute forwarding-rules create $FORWARDING_RULE \
    --load-balancing-scheme=EXTERNAL \
    --network-tier=PREMIUM \
    --address=$SVC_LB_IP \
    --target-https-proxy=$TARGET_HTTP_PROXY \
    --global \
    --ports=443
```

### Now we should create the subdomain and an A record

If we recheck the ssl certificate, it should be active within a few minutes.

```bash
# Check the status of the certificate
gcloud compute ssl-certificates list --global
```

### Configure the Cloud Run Service to be Accessible via Load Balancer

In addition to requiring an authorised user, this configuration prevents the service from even being exposed to the Internet:

```bash
gcloud run services update $SERVICE_NAME \
  --ingress internal-and-cloud-load-balancing \
  --region=$REGION
```

### Enable IAP on the Backend

```bash
gcloud compute backend-services update $BACKEND_SERVICE --global --iap=enabled
```

Now in Google Cloud Console: IAP, enable IAP on the backend service. Configure the Consent Screen.

```bash
gcloud run services update $SERVICE_NAME \
  --ingress internal-and-cloud-load-balancing \
  --region=$REGION
```

### Grant the Appropriate IAM Role to the End Users

Grant `IAP-secured web app user` to your user(s) or group(s). 

We can do this from the Cloud Console, or like this:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="group:gcp-devops@$MY_ORG" \
    --role="roles/iap.httpsResourceAccessor"
```
