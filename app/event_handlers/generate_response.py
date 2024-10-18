"""
File: login.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to generate response.
License: MIT License
"""

import re
import torch
import polars as pl
import gradio as gr
from gradio import ChatMessage

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_init import (
    cosine_similarity,
    sbert_model,
    puds_embeddings,
    puds_names,
    d_puds_cleaned,
    df_puds_skills,
)
from app.data_utils import get_embeddings, filter_unique_items, sort_subjects


def generate_subject_info(subject_info: list[str]) -> str:
    edu_level = (
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_LEVELS_EDUCATION_LABEL
        + "</span> <span class='value'>"
        + config_data.EducationLevels_ALL_LEVELS
        + "</span></div>"
        if not subject_info[6]
        or subject_info[6]
        in [
            config_data.Settings_PRIORITY[-1],
            config_data.Settings_PRIORITY[-2],
            config_data.EducationLevels_NONE_LEVELS,
        ]
        else "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_LEVEL_EDUCATION_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[6]}</span></div>"
    )

    subject_block = (
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_SUBJECT_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[1]}</span></div>"
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_ID_SUBJECT_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[0]}</span></div>"
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_DEPARTMENT_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[5]}</span></div>"
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_FACULTY_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[4]}</span></div>"
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_CAMPUS_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[3]}</span></div>"
        + edu_level
        + "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_AUDIENCE_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[8]}</span></div>"
        "<div class='info-item'><span class='label'>"
        + config_data.HtmlContent_FORMAT_LABEL
        + "</span> <span class='value'>"
        + f"{subject_info[9]}</span></div>"
    )

    return subject_block


def generate_skills(
    subject_id: str,
    max_skill_words: int,
) -> str:
    try:
        subject_skills = (
            df_puds_skills.filter(
                pl.col(config_data.DataframeHeaders_RU_ID) == int(subject_id)
            )[0]["LLM_Skills"][0]
            .strip()
            .split(";")
        )

        skills = [
            re.sub(r"[.,;:\s]+$", "", skill.strip()).capitalize()
            for skill in subject_skills
            if len(skill.split()) <= max_skill_words and skill.strip()
        ]

        if not skills:
            raise ValueError

        skills_content = "".join(
            [f"<span class='skill'>{skill}</span>" for skill in skills]
        )
        return (
            "<div class='info-skills'><span class='label'>"
            + config_data.HtmlContent_SKILLS_LABEL
            + "</span> <span class='value'>"
            + f"{skills_content}</span></div>"
        )

    except Exception:
        return (
            "<div class='info-skills-error'><span class='label'>"
            + config_data.InformationMessages_SKILLS_NOT_DEFINED
            + "</span></div>"
        )


def event_handler_generate_response(
    message: str,
    chat_history: list[ChatMessage],
    top_subjects: int,
    max_skill_words: int,
) -> tuple[gr.Textbox, list[ChatMessage]]:
    message = message.strip()

    if not message:
        return (gr.Textbox(value=None), chat_history)

    vacancy_embedding = get_embeddings(message, sbert_model)

    with torch.no_grad():
        similarities = (
            cosine_similarity(vacancy_embedding, puds_embeddings).cpu().tolist()
        )
        similarities = [
            (i, j) for i, j in zip(puds_names["names"].to_list(), similarities)
        ]

    sorted_subjects = sorted(similarities, key=lambda x: x[1], reverse=True)
    unique_subjects = filter_unique_items(sorted_subjects, top_subjects)

    all_top_items = []

    for subject, similarity in unique_subjects:
        match = next(
            (
                item
                for item in d_puds_cleaned
                if item.get(config_data.DataframeHeaders_RU_SUBJECTS[0]) == subject
            ),
            None,
        )

        if match:
            formatted_subject = (
                f"{match.get(config_data.DataframeHeaders_RU_ID, "-")} | {subject} | CS={similarity:.4f} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[2], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[1], "-")} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[3], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[4], "-")} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[5], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[6], "-")} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[7], "-")}"
            )
        else:
            formatted_subject = f"- | {subject} | CS={similarity:.4f}"

        all_top_items.append(formatted_subject)

    subjects_sorted = sort_subjects("; ".join(all_top_items))

    subject = list(map(str.strip, subject.split("|")))

    content = (
        "<div class='subject-info'>"
        + "".join(
            [
                "<div class='info'>"
                + f"{generate_subject_info(subject_info)}{generate_skills(subject_info[0], max_skill_words)}"
                + "</div>"
                for subject in subjects_sorted.split(";")
                if (subject_info := list(map(str.strip, subject.split("|"))))
            ]
        )
        + "</div>"
    )

    chat_history.append(ChatMessage(role="user", content=message))
    chat_history.append(ChatMessage(role="assistant", content=content))

    return (gr.Textbox(value=None), chat_history)
