""" Utility methods for downloading and uploading videos """
from dataclasses import dataclass
from io import BytesIO
import re

from pytubefix import YouTube
from pytubefix.cli import on_progress

import streamlit as st

@dataclass
class Video():
    """ Wrap the BytesIO objects and intended filenames. """
    data: BytesIO
    name: str
    
class DownloadError(Exception):
    """Custom exception for video download errors."""
    def __init__(self, message, url=None):
        super().__init__(message)
        self.url = url  # Optionally store the URL that caused the error

YT_REGEX = re.compile(r"^https:\/\/www\.youtube\.com\/watch\?v=[\w]*$")

@st.cache_data
def clean_filename(filename):
    """ Create a clean filename by removing unallowed characters. """
    pattern = r'[^a-zA-Z0-9._\s-]'
    cleaned_name = re.sub(pattern, '_', filename).replace("_ _", "_").replace("__", "_")
    return  cleaned_name

def get_video_id(url: str) -> str:
    """ Return the video ID, which is the part after 'v=' """
    return url.split("v=")[-1]

@st.cache_data
def is_valid_youtube_url(url):
    return YT_REGEX.match(url) is not None

@st.cache_data(ttl=3600, show_spinner=False) # We will use a dedicated spinner
def download_yt_video(url: str) -> Video:
    """ Download a YouTube video from the specified URL.
    The video content is read into a BytesIO object, which is then wrapped in a Video object and returned. """
    try:
        yt = YouTube(url, on_progress_callback=on_progress, client="WEB")
        video_stream = yt.streams.get_highest_resolution()
        if not video_stream:
            raise DownloadError("Stream not available", url)
        
        # YouTube resource titles may contain special characters which 
        # can't be used when saving the file. So we need to clean the filename.
        cleaned = clean_filename(yt.title)
        video_bytes = BytesIO()
        video_stream.stream_to_buffer(video_bytes)
        return Video(video_bytes, cleaned)
    except DownloadError as e:
        raise e
    except Exception as e:
        raise DownloadError(f"Download error: {e}", url=url) from e

@st.cache_data(ttl=3600)
def upload_video_bytesio(uploaded_file) -> Video:
    """ Upload the specified file and store as a BytesIO object.
    Wrap BytesIO object, and the filename, in a Video object.
    """
    file_contents = uploaded_file.read()
    video_bytes = BytesIO(file_contents)  # Create BytesIO from uploaded file data
    filename = clean_filename(uploaded_file.name)  # Sanitize the filename
    video = Video(video_bytes, filename)
    return video
