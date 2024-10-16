"""
File: data_init.py
Author: Dmitry Ryumin
Description: Initial data loading.
License: MIT License
"""

import torch

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_utils import load_puds_data, extract_embeddings
from app.load_models import load_sbert_model


cosine_similarity = torch.nn.CosineSimilarity()

df_puds_cleaned, df_puds_grouped = load_puds_data(
    directory=config_data.StaticPaths_PUDS,
    year=config_data.DataframeHeaders_SUBJECTS_YEAR,
    drop_duplicates=True,
    subset=config_data.DataframeHeaders_RU_SUBJECTS,
    full_info_cols=config_data.DataframeHeaders_SUBJECTS_FULL,
)
d_puds_cleaned = df_puds_cleaned.to_dicts()

sbert_model = load_sbert_model(config_data.Models_SBERT[0])

import time

start_time = time.time()

puds_embeddings, puds_names = extract_embeddings(d_puds_cleaned, sbert_model, 30)

end_time = time.time()
elapsed_time = end_time - start_time
