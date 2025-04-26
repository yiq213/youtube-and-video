# Video Intelligence (Youtube and Video) Application

<img src="docs/static/media/vid-intel-screenshot.png" alt="Video Intelligence Application" width="420" />

## Table of Contents

- [Overview](#overview)
- [Repo Metadata](#repo-metadata)
- [Repo Overview](#repo-overview)
- [Repo Structure](#repo-structure)
- [Overview of Jupyter Notebooks](#overview-of-jupyter-notebooks)
  - [Running the Jupyter Notebook Locally](#running-the-jupyter-notebook-locally)
  - [Running and Testing the Application Locally](#running-and-testing-the-application-locally)
- [Guidance for Running and Deploying the Video Intelligence Streamlit Application](#guidance-for-running-and-deploying-the-video-intelligence-streamlit-application)
  - [Every Session](#every-session)
  - [One-Time Google Cloud Setup](#one-time-google-cloud-setup)
  - [Running and Testing the Application Locally](#running-and-testing-the-application-locally)
  - [Running in Google Cloud](#running-in-google-cloud)
  - [Performance](#performance)
  - [Redeploying](#redeploying)
- [Optimising](#optimising)

## Repo Metadata

Author: Darren Lester

## Repo Overview

This repo describes an end-to-end journey. Briefly:

- We start with an idea. Here, the goal is to work with vidoes, which could be on YouTube. We want to be able to download videos, extract audio, transcribe, translate, and potentially summarise the content.
- We experiment on this idea, using a Jupyter notebook, with Python.
- We try out a few libraries and a couple of classical AI models. 
- Ultimately, we build a solution that makes use of Google Gemini multiomodal GenAI.
- Then we turn the notebook into a web application, using Streamlit.
- Then we package the application as a container.
- And finally, we host the application on Google Cloud's serverless Cloud Run service.

You can choose to follow / make use of any parts of this journey.

The journey is in three parts. Additionally, each part is supported with a walkthrough, which you can find on [Medium](https://medium.com/python-in-plain-english/downloading-youtube-videos-extracting-audio-and-generating-transcripts-with-python-and-jupyter-c3068f82bbe0).

### Part 1: [youtube-demos.ipynb](src/notebooks/youtube-demos.ipynb)

<img src="docs/static/media/notebook.png" alt="MVP notebook" width="420" />

In this notebook I demonstrate:

- A Jupyter notebook that provides a minimum viable product for a YouTube video downloader application.
- How to quickly setup and use the notebook, including how to run it with zero install effort, in Google Colab.
- Three different ways to download YouTube videos and extract audio to mp3.
- Using the Python Speech Recognition library, along with the Google Speech Recognition API, to transcribe mp3 audio into text.
- Extracting pre-existing transcripts from YouTube videos, and how to translate such transcripts.

See [walkthrough](https://medium.com/python-in-plain-english/downloading-youtube-videos-extracting-audio-and-generating-transcripts-with-python-and-jupyter-c3068f82bbe0).

### Part 2: [youtube-demos-with-google-ai.ipynb](src/notebooks/youtube-demos-with-google-ai.ipynb)

- Using the Google Video Intelligence API to provide more reliable and more accurate trancription.
- Using Google Gemini Generative AI to transcribe, translate and summarise video content.
- How to build your Jupyter notebook so it can run locally, in Google Colab, or in Google Vertex AI Workbench.

See [walkthrough](https://python.plainenglish.io/youtube-video-downloader-with-generative-ai-and-python-run-anywhere-transcribe-and-translate-dec2e593dd58).

### Part 3: [video-intelligence-streamlit](src/video-intelligence-streamlit/)

<img src="docs/static/media/vid-intel-architecture.png" alt="Video Intelligence Architecture" width="420" />

- Provide a UI in the form of a Streamlit application
- Containerise the application using Docker
- Host the application on Google Cloud Run

See [walkthrough](https://medium.com/google-cloud/running-ai-youtube-and-video-processing-as-a-python-streamlit-web-application-and-hosting-on-748aae8e54b4).

## Repo Structure

```text
project/
├── deploy/
|   ├── tf/              # Terraform to build infra
|   └── cloudbuild.yaml  # Google Cloud Build configuration
|
├── src/
|   └── notebooks/       # Experimentation Jupyter notebooks
|   └── video-intelligence-streamlit/
|       ├── app.py
|       ├── Dockerfile
|       ├── requirements.txt
|       └── video_utils.py
|
├── .env # Local environment variables used in scripts
├── .gitattributes
├── .gitignore
├── README.md            # Project guidance
└── requirements.txt
```

## Overview of Jupyter Notebooks

If you don't know much about Jupyter notebooks, then I suggest you start with my article [here](https://medium.com/python-in-plain-english/five-ways-to-run-jupyter-labs-and-notebooks-23209f71e5c0), which covers:

- The value and point of Jupyter notebooks.
- Good use cases for Jupyter notebooks.
- Several ways to run the notebooks
- How to run your own - or someone else's notebooks (like the ones in this repo) - quickly and easily, _for free_ in [Google Colab](https://colab.research.google.com/).

### Running the Jupyter Notebook Locally

Here we create a Python virtual environment, install Jupyter notebook to the environment, and then run our notebooks from there.

```bash
py -m pip install --upgrade pip

# Create virtual env, if you haven't already
py -m venv .venv

# Activate the venv
./.venv/Scripts/activate

# Install requirements - i.e. notebook
py -m pip install -r requirements.txt
```

Now you can use your venv as your Jupyter kernel.

## Guidance for Running and Deploying the Video Intelligence Streamlit Application

### Every Session

For local dev, always set these variables:

```bash
# Authenticate yourself to gcloud
# And also setup ADC so any locally running application can access Google APIs
# Note that credentials will be saved to 
# ~/.config/gcloud/application_default_credentials.json
gcloud auth login --update-adc 

# Set these manually...
export PROJECT_ID="<Your Google Cloud Project ID>"
export REGION="<your region>"
export MY_ORG="<enter your org domain>"
export DOMAIN_NAME="<enter application domain name>"

# Or load from .env
source .env

export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

export LOG_LEVEL='DEBUG'
export REPO=video-intelligence
export SERVICE_NAME=video-intelligence

# Check we're in the correct project
gcloud config list project

# If we're on the wrong project...
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID
gcloud config list project
```

### One-Time Google Cloud Setup

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

### Running and Testing the Application Locally

#### Per-Environment Setup

```
# Setup Python environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Running Streamlit App

```bash
# Local streamlit app
streamlit run app.py --browser.serverAddress=localhost
```

#### Running in a Local Container

```bash
# Get a unique version to tag our image
export VERSION=$(git rev-parse --short HEAD)

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

### Running in Google Cloud

#### Build and Push to Google Artifact Registry:

```bash
# One time setup - create a GAR repo
gcloud artifacts repositories create "$REPO" \
  --location="$REGION" --repository-format=Docker

# Allow authentication to the repo
gcloud auth configure-docker "$REGION-docker.pkg.dev"

# Every time we want to build a new version and push to GAR
# This will take a couple of minutes
export VERSION=$(git rev-parse --short HEAD)
gcloud builds submit \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION"
```

#### Deploy to Cloud Run

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
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=$LOG_LEVEL

APP_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format="value(status.address.url)")

### Create the External Application Load Balancer

```bash
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

# Or regional
gcloud compute addresses create regional-lb-ip \
    --project=$PROJECT_ID \
    --network-tier=STANDARD \
    --region=$REGION

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

#### Now we should create the subdomain and an A record

If we recheck the ssl certificate, it should be active within a few minutes.

```bash
# Check the status of the certificate
gcloud compute ssl-certificates list --global
```

#### Configure the Cloud Run Service to be Accessible via Load Balancer

In addition to requiring an authorised user, this configuration prevents the service from even being exposed to the Internet:

```bash
gcloud run services update $SERVICE_NAME \
  --ingress internal-and-cloud-load-balancing \
  --region=$REGION
```

#### Setup IAP Access

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

#### Enable IAP on the Backend

```bash
gcloud compute backend-services update $BACKEND_SERVICE --global --iap=enabled
```

Now in Google Cloud Console: IAP, enable IAP on the backend service. Configure the Consent Screen.

#### Grant the Appropriate IAM Role to the End Users

Grant `IAP-secured web app user` to your user(s) or group(s). 

We can do this from the Cloud Console, or like this:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="group:gcp-devops@$MY_ORG" \
    --role="roles/iap.httpsResourceAccessor"
```

### Performance

```bash
gcloud beta run services update $SERVICE_NAME \
  --region=$REGION --cpu-boost
```

### Redeploying

```bash
# Let's set logging level to INFO rather than DEBUG
export LOG_LEVEL='INFO'
export VERSION=$(git rev-parse --short HEAD)

gcloud builds submit \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION"

# Deploy to Cloud Run - this takes a couple of minutes
gcloud run deploy "$SERVICE_NAME" \
  --project=$PROJECT_ID \
  --port=8080 \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION" \
  --max-instances=1 \
  --no-allow-unauthenticated \
  --region=$REGION \
  --platform=managed  \
  --ingress internal-and-cloud-load-balancing \
  --cpu-boost \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=$LOG_LEVEL
  ```

## Optimising

We want to eliminate the LB.

```bash
# Or load from .env
source ../../.env
export LOG_LEVEL='INFO'
export VERSION=$(git rev-parse --short HEAD)

# Allow the service to be public - we can't use allAuthenticatedUsers
# If we want authenticated users, we'll need to implement OAuth in the application
# E.g. https://developers.google.com/identity/protocols/oauth2/web-server
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --member="allUsers"  \
  --region=$REGION \
  --role="roles/run.invoker"

# Allow public access, without using the LB
gcloud run services update $SERVICE_NAME \
  --ingress all \
  --region=$REGION

# Or to redeploy
# Deploy to Cloud Run - this takes a couple of minutes
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$VERSION" \
  --max-instances=1 \
  --allow-unauthenticated \
  --region=$REGION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --ingress all \
  --cpu-boost \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOG_LEVEL=$LOG_LEVEL
```
