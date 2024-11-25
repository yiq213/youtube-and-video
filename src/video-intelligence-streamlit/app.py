import streamlit as st

import io
import logging
import os
import re
import dazbo_commons as dc

from pytubefix import YouTube
from pytubefix.cli import on_progress
import youtube_transcript_api as yt_api

from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage

import vertexai # Google Cloud Vertex Generative AI SDK for Python
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

APP_NAME = "dazbo-vid-intel-streamlit"
MODEL_NAME = "gemini-1.5-flash-002"

# Set env vars
PROJECT_ID = os.environ.get('PROJECT_ID')
REGION = os.environ.get('REGION')

# Configure logging
logger = dc.retrieve_console_logger(APP_NAME)
logger.setLevel(logging.DEBUG)
logger.info("Logger initialised.")
logger.debug("DEBUG level logging enabled.")

def configure_locations(app_name: str):
    locations = dc.get_locations(app_name)
    for attribute, value in vars(locations).items():
        logger.debug(f"{attribute}: {value}")

def clean_filename(filename):
    """ Create a clean filename by removing unallowed characters. """
    pattern = r'[^a-zA-Z0-9._\s-]'
    cleaned_name = re.sub(pattern, '_', filename).replace("_ _", "_").replace("__", "_")
    return  cleaned_name

def get_video_id(url: str) -> str:
    """ Return the video ID, which is the part after 'v=' """
    return url.split("v=")[-1]

# For local dev, you may need to:
# gcloud auth login
# gcloud auth application-default login
# gcloud auth application-default set-quota-project $PROJECT_ID
def google_adc_auth():
    logger.debug("Retrieving ADC")
    try:
        credentials, _ = default() # Retrieve ADC
    except DefaultCredentialsError as e:
        logger.error(e)

    return credentials

def upload_to_gcs(bucket:str, src_file, dest_name):
    """ Upload a file to a GCS bucket. """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket)
        
        # Destination blob name
        blob_name = dest_name 
        blob = bucket.blob(blob_name)
        logger.info(f"Uploading {src_file} to gs://{bucket}/{blob_name}")
        blob.upload_from_filename(src_file) 
        
        return f"gs://{bucket}/{blob_name}" # Return the full GCS URI
    except Exception as e:
        logger.exception(f"Error uploading {src_file} to GCS: {e}")
        return

# def get_gcs_uris(bucket_name:str, glob:str=None) -> list[str]:
#     """
#     Retrieves bucket URIs for files in a specified folder, 
#     optionally matching a wildcard glob.

#     Args:
#         bucket_name: The name of the GCS bucket.
#         glob: A wildcard string to match filenames (e.g., '*.mp4').

#     Returns:
#         A list of bucket URIs for matching files.
#     """
#     logger.debug(f"Listing blobs in {bucket_name}/{glob if glob else ''}...")
#     client = storage.Client() # Uses ADC so we don't have to pass in credentials

#     blobs = client.list_blobs(bucket_or_name=bucket_name, 
#                               match_glob=glob)
#     return [f"gs://{bucket_name}/{blob.name}" for blob in blobs]

@st.cache_resource
def load_models():
    logger.debug(f"Initialisomg Vertex AI")    
    vertexai.init(project=PROJECT_ID, location=REGION)
    
    logger.debug(f"Loading model {MODEL_NAME}")
    model = GenerativeModel(MODEL_NAME)
    return model

def main():
    logger.debug(f"{PROJECT_ID=}")
    logger.debug(f"{REGION=}")
    configure_locations(APP_NAME)

    credentials = google_adc_auth() # Might not need this
    model = load_models()
    
    st.header("Video Intelligence", divider="rainbow")

    response = model.generate_content("Write a story about a silly black and white cat called Mycroft")
    logger.debug(response.text)

if __name__ == "__main__":
    main()