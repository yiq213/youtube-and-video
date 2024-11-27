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
import textwrap
import dazbo_commons as dc

import streamlit as st

from google.api_core.exceptions import ServiceUnavailable
import vertexai # Google Cloud Vertex Generative AI SDK for Python
from vertexai.generative_models import GenerativeModel, Part

from video_utils import ( 
    download_yt_video,
    DownloadError,
    is_valid_youtube_url,
    upload_video_bytesio,
#    get_video_id
)

APP_NAME = "dazbo-vid-intel-streamlit"
MODEL_NAME = "gemini-1.5-flash-002"

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
            download_spinner = st.spinner("Downloading video...")
        
        with st.container(border=True):
            uploaded_file = st.file_uploader("Or Upload a Video File:")
            upload_btn = st.button("Upload video", key="upload_btn")
        
        if load_yt_btn:
            # TODO: Display some metadata on yt or local vid load
            if youtube_url:
                if is_valid_youtube_url(youtube_url):
                    with download_spinner:
                        try:
                            logger.info(f"Downloading yt video {youtube_url}")
                            video = download_yt_video(youtube_url)
                            st.session_state.video = video
                        except DownloadError as e:
                            st.error(str(e))   
                            logger.error(f"Error processing URL '{e.url}'.")
                else:
                    st.error("URL is not a valid YouTube URL.")
                    del st.session_state.video
            else:
                logger.warn("Please specify a YouTube video to load.")

        if upload_btn:
            if uploaded_file:
                logger.info(f"Uploading from local file {uploaded_file}")
                video = upload_video_bytesio(uploaded_file)
                st.session_state.video = video
            else:
                logger.warn("Please specify a video to load.")
    
        if  "video" in st.session_state:
            video = st.session_state.video
            st.video(video.data, format="video/mp4")
        else:
            st.write("No video loaded.")
            
    response_container = st.container(border=True)
    with response_container:
        try:
            # TODO: Let's safeguard the video length
            transcribe_and_summarise = st.button("Transcribe and Summarise", key="transcribe_and_summarise")
            if transcribe_and_summarise: # button pressed
                    
                # Lazy instantiation of the model
                if "model" not in st.session_state:
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
                            - If this is a song, please provide a summary of the words, and your interpretation of the meaning.
                            - If there is enough content in the transcription to make it worthwhile, please provide topic titles and topic summaries.
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
