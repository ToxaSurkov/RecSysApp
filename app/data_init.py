"""
File: data_init.py
Author: Dmitry Ryumin
Description: Initial data loading.
License: MIT License
"""

import torch

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_utils import load_parquet
from app.load_models import SbertModelManager


cosine_similarity = torch.nn.CosineSimilarity()

df_puds_skills = load_parquet(
    path=config_data.Path_APP / config_data.StaticPaths_PUDS_SKILLS,
    drop_duplicates=True,
    subset=config_data.DataframeHeaders_RU_ID,
)

model_manager_sbert = SbertModelManager()
# model_manager_sbert.change_model(config_data.Models_SBERT[0])
