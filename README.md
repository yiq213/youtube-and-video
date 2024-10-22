# Youtube and Video

## Repo Overview

Here you will find examples of how to work with YouTube videos using Python. I will demonstrate:

- How to download videos and extract audio.
- How to transcribe audio to text using a speech-to-text API
- How to extract existing transcripts and translate

**This is work-in-progress.  Content coming soon!**

## Future Plan

- Google Speech-to-Text API
- Google Video Intelligence API
- Gemini Pro Generative AI
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

#### Method 1 - Use a Python Virtual Env with Notebook Installed

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

#### Method 2 - Running Local Jupyter Lab Container

You can use my `docker-compose-scipy-lab.yml` to run a local Docker container running a Jupyter SciPy lab container.

```bash
# To launch the container
docker compose -f ./docker-compose-scipy-lab.yml up -d

# To stop it
docker compose -f ./docker-compose-scipy-lab.yml down
```

