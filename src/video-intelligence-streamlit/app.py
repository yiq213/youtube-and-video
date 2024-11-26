""" 
Streamlit application for processing uploaded videos, or YouTube videos.
It transcribes audio and - if necessary - translates.
Makes use of Google Gemini multimodal model for transcription and translation.

For local dev, you may need to set ADC:
gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT_ID 
"""
import logging
import os
import re
import textwrap
from dataclasses import dataclass
from io import BytesIO
import dazbo_commons as dc

import streamlit as st

from pytubefix import YouTube
from pytubefix.cli import on_progress

from google.api_core.exceptions import ServiceUnavailable
import vertexai # Google Cloud Vertex Generative AI SDK for Python
from vertexai.generative_models import GenerativeModel, Part

APP_NAME = "dazbo-vid-intel-streamlit"
MODEL_NAME = "gemini-1.5-flash-002"
YT_REGEX = re.compile(r"^https:\/\/www\.youtube\.com\/watch\?v=[\w]*$")

# Set env vars
PROJECT_ID = os.environ.get('PROJECT_ID', None)
REGION = os.environ.get('REGION', None)

if not REGION and not PROJECT_ID:
    raise ValueError("Environment variables not properly set.")

TEST_VIDEOS = [
    "https://www.youtube.com/watch?v=udRAIF6MOm8",  # Sigrid - Burning Bridges (English)
    "https://www.youtube.com/watch?v=CiTn4j7gVvY",  # Melissa Hollick - I Believe (English)
    "https://www.youtube.com/watch?v=nLgHNu2N3JU",  # Jim Carey - Motivational speech (English)
    "https://www.youtube.com/watch?v=d4N82wPpdg8",  # Jerry Heil & Alyona Alyona - Teresa & Maria (Ukrainian)
]

@dataclass
class Video():
    """ Wrap the BytesIO objects and intended filenames. """
    data: BytesIO
    name: str

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

@st.cache_data
def clean_filename(filename):
    """ Create a clean filename by removing unallowed characters. """
    pattern = r'[^a-zA-Z0-9._\s-]'
    cleaned_name = re.sub(pattern, '_', filename).replace("_ _", "_").replace("__", "_")
    return  cleaned_name

@st.cache_data
def get_video_id(url: str) -> str:
    """ Return the video ID, which is the part after 'v=' """
    return url.split("v=")[-1]

@st.cache_data
def is_valid_youtube_url(url):
    return YT_REGEX.match(url) is not None

@st.cache_data(ttl=3600)
def download_yt_video(url: str) -> Video:
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
        logger.debug("Done")
        return Video(video_bytes,cleaned)
    except Exception as e:
        st.error("Error downloading video.")   
        logger.error(f"Error processing URL '{url}'.")
        logger.error(f"The cause was: {e}") 
    
    return None

@st.cache_data(ttl=3600)
def upload_video(uploaded_file):
    file_contents = uploaded_file.read()
    video_bytes = BytesIO(file_contents)  # Create BytesIO from uploaded file data
    filename = clean_filename(uploaded_file.name)  # Sanitize the filename
    video = Video(video_bytes, filename)
    return video

@st.cache_resource
def load_model(model_name: str):
    """ Load AI model """
    logger.debug("Initialising Vertex AI")    
    vertexai.init(project=PROJECT_ID, location=REGION)
    
    logger.debug(f"Loading model {model_name}")
    try:
        model = GenerativeModel(model_name)
        logger.debug("Model loaded.")
        return model
    except Exception as e:
        st.error("Error loading model. Aborting.")
        logger.error(e)
        raise e

def main():
    logger.debug(f"{PROJECT_ID=}")
    logger.debug(f"{REGION=}")
    
    st.header("Dazbo's Video Intelligence", divider="rainbow")
    
    video_container = st.container(border=True)
    with video_container:
        with st.container(border=True):
            youtube_url = st.text_input("Enter YouTube URL:", value=TEST_VIDEOS[0])
            load_yt_btn = st.button("Load video from YouTube", key="load_yt_btn")
        
        with st.container(border=True):
            uploaded_file = st.file_uploader("Or Upload a Video File:")
            upload_btn = st.button("Upload video", key="upload_btn")
        
        if load_yt_btn:
            # TODO: Display some metadata on yt or local vid load
            if youtube_url:
                if is_valid_youtube_url(youtube_url):
                    progress_state = st.text('Downloading video')
                    video = download_yt_video(youtube_url)
                    st.session_state.video = video
                    progress_state.text('Done!')
                else:
                    st.error("URL is not a valid YouTube URL.")
                    del st.session_state.video
            else:
                logger.warn("Please specify a YouTube video to load.")

        if upload_btn:
            if uploaded_file:
                video = upload_video(uploaded_file)
                st.session_state.video = video
            else:
                logger.warn("Please specify a video to load.")
    
        if  "video" in st.session_state:
            video = st.session_state.video
            st.video(video.data, format="video/mp4")
        else:
            st.write("No video downloaded.")
            
    response_container = st.container(border=True)
    with response_container:
        try:
            # TODO: Let's safeguard the video length
            transcribe_and_summarise = st.button("Transcribe and Summarise", key="transcribe_and_summarise")
            if transcribe_and_summarise: # button pressed
                    
                # Lazy instantiation of the model
                if "model" not in st.session_state:
                    logger.debug("Initialising session variables")
                    st.session_state["model"] = load_model(MODEL_NAME)
                
                model = st.session_state["model"]
                
                logger.debug("Transcribing and summarising button pressed")
                if "video" in st.session_state:
                    with st.spinner("Asking the AI..."):
                        video = st.session_state.video
                        video_data = Part.from_data(data=video.data.getvalue(), mime_type="video/mp4")

                        prompt = textwrap.dedent("""\
                            In this video, please:
                            - Transcribe any spoken or sung words.
                            - If the words are English, write them in English.
                            - If the words are in another language, write them in the native language, and then show me the English translation.
                            - If any significant proportion of the words are not English, tell me what the language is.
                            - Provide a summary of the words, and your interpretation of the meaning.
                        """)
                        contents = [prompt, video_data] # multimodal input

                        logger.debug(f"Prompt:\n{prompt}")
                        logger.debug("Asking the model. Please wait...")
                        response = model.generate_content(contents, stream=False)
                        with st.chat_message("ai"):
                            st.markdown(response.text)
                else:
                    st.error("Please download a video first.")
        except ServiceUnavailable as e:
            logger.error(e)
            st.error("Error calling AI service. Please wait a few seconds and try again.")
        except Exception as e:
            logger.error(e)
            st.error(e)
            
if __name__ == "__main__":
    main()
