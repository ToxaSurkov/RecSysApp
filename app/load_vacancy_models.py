"""
File: load_models.py
Author: Dmitry Ryumin
Description: Classes for loading models and updating embeddings.
License: MIT License
"""

import torch
from transformers import AutoTokenizer, AutoModel
from scipy.spatial.distance import cosine
import pandas as pd
import numpy as np
from collections import Counter

# Importing necessary components for the Gradio app
from app.config import config_data


def parse_embedding_from_str(str_emb):
    emb = []
    for part in str_emb.strip()[1:-1].split(" "):
        fixed_part = part.strip()
        if len(fixed_part) > 0:
            emb.append(float(fixed_part))

    return emb


def load_embeddings(path):
    df = pd.read_csv(path)
    all_embs = []
    all_key_skills = []
    for _, row in df.iterrows():  # tqdm(df.embedding):
        all_embs.append(parse_embedding_from_str(row["embedding"]))
        all_key_skills.append(eval(row["key_skills"]))

    df["embedding"] = all_embs
    df["key_skills"] = all_key_skills

    return df


class EmbeddingExtractor:
    def __init__(self, model, tokenizer, initial_df, similarity_metric=cosine):
        self.embeddings = {}
        self.model = model
        self.tokenizer = tokenizer
        self.similarity_metric = similarity_metric

        self._initialize_embeddings(initial_df)

    def _initialize_embeddings(self, initial_df):
        for _, row in initial_df.iterrows():
            name = row["name"]
            emb = row["embedding"]

            self.embeddings[name] = emb

    def extract(self, text):
        if text in self.embeddings:
            return self.embeddings[text]

        encoded_input = self.tokenizer(
            [text], padding=True, truncation=True, max_length=64, return_tensors="pt"
        )
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        embedding = model_output.pooler_output[0].numpy().astype(np.float32)

        self.embeddings[text] = embedding

        return embedding

    def extract_batch(self, texts):
        encoded_input = self.tokenizer(
            texts, padding=True, truncation=True, max_length=64, return_tensors="pt"
        )
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        for i in range(len(texts)):
            text = texts[i]
            embedding = model_output.pooler_output[i]

            self.embeddings[text] = embedding

    def similarity(self, emb1, emb2):
        return 1 - self.similarity_metric(emb1, emb2)


class VacancyFinder:
    def __init__(self, embedding_extractor, initial_df):
        self.embedding_extractor = embedding_extractor
        self.titles = {}
        self.vacancy_stats_by_title = {}

        self._load_vacancies(initial_df)

    def _load_vacancies(self, initial_df):
        titles = list(set(initial_df.parent.values))

        for title in titles:
            self.titles[title] = self.embedding_extractor.extract(title)
            self.vacancy_stats_by_title[title] = []
            for _, row in initial_df.iterrows():
                name = row["name"]
                key_skills = row["key_skills"]
                id_ = row["id"]

                self.vacancy_stats_by_title[title].append(
                    [name, key_skills, id_, self.embedding_extractor.extract(name)]
                )

    def _select_best_titles(self, emb, amount):
        stats = []
        for title_name, title_emb in self.titles.items():
            stats.append(
                [
                    title_name,
                    title_emb,
                    self.embedding_extractor.similarity(emb, title_emb),
                ]
            )

        return sorted(stats, key=lambda x: -x[-1])[:amount]

    def _select_best_vacancies(self, emb, titles, amount):
        stats = []
        for title in titles:
            for (
                vacancy_name,
                key_skills,
                vacancy_id,
                vacancy_emb,
            ) in self.vacancy_stats_by_title[title]:
                stats.append(
                    [
                        vacancy_name,
                        key_skills,
                        vacancy_id,
                        vacancy_emb,
                        title,
                        self.embedding_extractor.similarity(emb, vacancy_emb),
                    ]
                )

        return sorted(stats, key=lambda x: -x[-1])[:amount]

    def get_best_vacancies(self, vacancy_name, nearest_titles=3, amount=20):
        emb = self.embedding_extractor.extract(vacancy_name)
        titles = self._select_best_titles(emb, nearest_titles)
        title_names = [title_name for title_name, _, _ in titles]

        best_vacancies = self._select_best_vacancies(emb, title_names, amount)
        return best_vacancies


def aggregate_skills(all_skills):
    skills_list = []
    for key_skills in all_skills:
        skills_list.extend(key_skills)

    return Counter(skills_list)


class SkillsExtractor:

    def __init__(
        self,
        path_to_vacancies_info,
        model_path=str(
            config_data.Path_APP
            / config_data.StaticPaths_MODELS
            / config_data.Models_SBERT_VACANCY[0]
        ),
        tokenizer_path=str(
            config_data.Path_APP
            / config_data.StaticPaths_MODELS
            / config_data.Models_SBERT_VACANCY[0]
        ),
    ):
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        model = AutoModel.from_pretrained(model_path)
        emb_df = load_embeddings(path_to_vacancies_info)
        embedding_extractor = EmbeddingExtractor(model, tokenizer, emb_df)

        self.vacancy_finder = VacancyFinder(embedding_extractor, emb_df)

    def key_skills_for_profession(
        self, profession, max_skills=100, min_frequency=3, nearest_vacancies=50
    ):
        all_key_skills = []
        for _, key_skills, _, _, _, _ in self.vacancy_finder.get_best_vacancies(
            profession, amount=nearest_vacancies
        ):
            all_key_skills.append(key_skills)

        selected_skills = []
        for name, amount in aggregate_skills(all_key_skills).most_common():
            if len(selected_skills) >= max_skills or amount < min_frequency:
                break
            else:
                selected_skills.append(name)

        return selected_skills
