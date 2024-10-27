"""
File: data_init.py
Author: Dmitry Ryumin
Description: Initial data loading.
License: MIT License
"""

import time

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_utils import load_parquet
from app.load_models import SbertModelManager
from app.load_vacancy_models import SkillsExtractor


df_puds_skills = load_parquet(
    path=config_data.Path_APP / config_data.StaticPaths_PUDS_SKILLS,
    drop_duplicates=True,
    subset=config_data.DataframeHeaders_RU_ID,
)

model_manager_sbert = SbertModelManager()
model_manager_sbert.change_model(config_data.Models_SBERT_PUDS[0])

start_time = time.time()

skills_extractor = SkillsExtractor(
    path_to_vacancies_info=config_data.Path_APP / config_data.StaticPaths_VACANCY_CSV
)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Время выполнения: {elapsed_time:.6f} секунд")
