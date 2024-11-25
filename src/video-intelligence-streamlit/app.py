import logging
import os
import re
import textwrap
from dataclasses import dataclass
from io import BytesIO
from typing import Optional
import dazbo_commons as dc

import streamlit as st

from pytubefix import YouTube
from pytubefix.cli import on_progress

from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import ServiceUnavailable

import vertexai # Google Cloud Vertex Generative AI SDK for Python
from vertexai.generative_models import GenerativeModel, Part

APP_NAME = "dazbo-vid-intel-streamlit"
MODEL_NAME = "gemini-1.5-flash-002"

# Set env vars
PROJECT_ID = os.environ.get('PROJECT_ID')
REGION = os.environ.get('REGION')

TEST_VIDEOS = [
    "https://www.youtube.com/watch?v=udRAIF6MOm8",  # Sigrid - Burning Bridges (English)
    "https://www.youtube.com/watch?v=CiTn4j7gVvY",  # Melissa Hollick - I Believe (English)
    "https://www.youtube.com/watch?v=nLgHNu2N3JU",  # Jim Carey - Motivational speech (English)
    "https://www.youtube.com/watch?v=d4N82wPpdg8",  # Jerry Heil & Alyona Alyona - Teresa & Maria (Ukrainian)
]

@dataclass
class VideoAudioData():
    """ Wrap the BytesIO objects and intended filenames for video and audio streams. """
    video: BytesIO
    audio: Optional[BytesIO]  # Allow for cases where audio isn't present
    video_file_name: str
    audio_file_name: Optional[str] # Match optionality of audio

# Configure logging
if st.session_state.get("logger") is None:
    st.session_state["logger"] = dc.retrieve_console_logger(APP_NAME)

logger = st.session_state["logger"]
logger.setLevel(logging.DEBUG)
logger.info("Logger initialised.")
logger.debug("DEBUG level logging enabled.")

@st.cache_data(ttl=3600)
def configure_locations(app_name: str):
    locations = dc.get_locations(app_name)
    for attribute, value in vars(locations).items():
        logger.debug(f"{attribute}: {value}")
        
    return locations

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
@st.cache_resource
def google_adc_auth():
    logger.debug("Retrieving ADC")
    try:
        credentials, _ = default() # Retrieve ADC
    except DefaultCredentialsError as e:
        logger.error(e)

    return credentials

@st.cache_data(ttl=3600)
def download_yt_video(url: str) -> VideoAudioData:
    logger.info(f"Downloading video {url}")

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video_stream = yt.streams.get_highest_resolution()
        if not video_stream:
            raise Exception("Stream not available.")
        
        # YouTube resource titles may contain special characters which 
        # can't be used when saving the file. So we need to clean the filename.
        cleaned = clean_filename(yt.title)
        
        logger.info(f"Downloading video as {cleaned}.mp4")
        video_bytes = BytesIO()
        video_stream.stream_to_buffer(video_bytes)
    
        logger.info("Creating audio bytes")
        audio_stream = yt.streams.get_audio_only()
        audio_bytes = BytesIO()
        audio_stream.stream_to_buffer(audio_bytes)
        
        logger.debug("Done")
        return VideoAudioData(video=video_bytes, 
                              audio=audio_bytes, 
                              video_file_name=f"{cleaned}.mp4", 
                              audio_file_name=f"{cleaned}.m4a"
        )

    except Exception as e:        
        logger.error(f"Error processing URL '{url}'.")
        logger.debug(f"The cause was: {e}") 
    
    return None

@st.cache_resource
def load_models():
    logger.debug("Initialising Vertex AI")    
    vertexai.init(project=PROJECT_ID, location=REGION)
    
    logger.debug(f"Loading model {MODEL_NAME}")
    model = GenerativeModel(MODEL_NAME)
    logger.debug("Model loaded.")
    return model

def main():
    logger.debug(f"{PROJECT_ID=}")
    logger.debug(f"{REGION=}")
    
    if st.session_state.get("model") is None:
        logger.debug("Initialising session variables")
        st.session_state["credentials"] = google_adc_auth()
        st.session_state["model"] = load_models()
    else:
        logger.debug("Session variables already initialised")
    
    credentials = st.session_state["credentials"]
    model = st.session_state["model"]
    
    st.header("Video Intelligence", divider="rainbow")
    
    download_video = st.button("Download Video", key="download_video")
    if download_video:
        progress_state = st.text('Downloading video and extracting audio...')
        video_and_audio = download_yt_video(TEST_VIDEOS[0])
        logger.debug("Adding video_and_audio to session state")
        st.session_state.video_and_audio = video_and_audio
        progress_state.text('Done!')
        
        st.video(video_and_audio.video, format="video/mp4")

    try:
        transcribe_and_summarise = st.button("Transcribe and Summarise", key="transcribe_and_summarise")
        if transcribe_and_summarise:
            logger.debug("Transcribing and summarising button pressed")
            if st.session_state.get("video_and_audio") is not None:
                with st.spinner("Asking the model..."):
                    video_and_audio = st.session_state.video_and_audio
                    audio = Part.from_data(data=video_and_audio.audio.getvalue(), mime_type="audio/mpeg")
                    
                    prompt = textwrap.dedent("""\
                        In this audio file, please tell me:
                        - What languages are being sung?
                        - What are the lyrics? Please show me in the native language, and translated to English.
                        - What is the meaning of the lyrics?
                    """)
                    contents = [prompt, audio] # multimodal input

                    logger.debug(f"Prompt:\n{prompt}")
                    logger.debug("Asking the model. Please wait...")
                    response = model.generate_content(contents, stream=False)
                    st.markdown(response.text)
            else:
                st.error("Please download a video first.")
    except ServiceUnavailable as e:
        logger.error(e)
        st.error(f"""Error calling AI service:  
                 {e.message}""")

if __name__ == "__main__":
    main()
