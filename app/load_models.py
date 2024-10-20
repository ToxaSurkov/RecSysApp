"""
File: load_models.py
Author: Dmitry Ryumin
Description: Functions for loading models.
License: MIT License
"""

from sentence_transformers import SentenceTransformer
from pathlib import PosixPath

# Importing necessary components for the Gradio app
from app.gpu_init import device
from app.config import config_data


def load_sbert_model(model_name: PosixPath) -> SentenceTransformer:
    sbert_model = SentenceTransformer(
        model_name_or_path=str(
            config_data.Path_APP / config_data.StaticPaths_MODELS / model_name
        ),
        device=device,
        local_files_only=True,
        trust_remote_code=True,
    )

    return sbert_model
