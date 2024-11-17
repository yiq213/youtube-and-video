# Youtube and Video

## Repo Overview

Here you will find examples of how to work with YouTube videos using Python and various APIs. 

### Part 1: [youtube-demos.ipynb](src/notebooks/youtube-demos.ipynb)

In this notebook I demonstrate:

- A Jupyter notebook that provides a minimum viable product for a YouTube video downloader application.
- How to quickly setup and use the notebook, including how to run it with zero install effort, in Google Colab.
- Three different ways to download YouTube videos and extract audio to mp3.
- Using the Python Speech Recognition library, along with the Google Speech Recognition API, to transcribe mp3 audio into text.
- Extracting pre-existing transcripts from YouTube videos, and how to translate such transcripts.

### Part 2: [youtube-demos-with-google-ai.ipynb](src/notebooks/youtube-demos-with-google-ai.ipynb)

- Using the Google Video Intelligence API to provide more reliable and more accurate trancription.
- Using Google Gemini Generative AI to transcribe, translate and summarise video content.
- How to build your Jupyter notebook so it can run locally, in Google Colab, or in Google Vertex AI Workbench.

## Future Plan

- Convering to a Streamlit application
- Hosting on Google Cloud Run
- Terraform

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

