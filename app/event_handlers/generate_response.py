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
from app.data_init import cosine_similarity, df_puds_skills, model_manager_sbert
from app.data_utils import get_embeddings, filter_unique_items, sort_subjects


def create_html_block(label: str, value: str) -> str:
    return f"<div class='info-item'><span class='label'>{label}</span> <span class='value'>{value}</span></div>"


def determine_edu_level(subject_info: list[str]) -> tuple[str, str]:
    if not subject_info[6] or subject_info[6] in [
        config_data.Settings_PRIORITY[-1],
        config_data.Settings_PRIORITY[-2],
        config_data.EducationLevels_NONE_LEVELS,
    ]:
        edu_level_label = config_data.HtmlContent_LEVELS_EDUCATION_LABEL
        edu_level = config_data.EducationLevels_ALL_LEVELS
    else:
        edu_level_label = config_data.HtmlContent_LEVEL_EDUCATION_LABEL
        edu_level = subject_info[6]

    return edu_level_label, edu_level


def generate_subject_info(
    subject_info: list[str], edu_level_label: str, edu_level: str
) -> str:
    number_education_block = (
        create_html_block(
            (
                config_data.HtmlContent_NUMBERS_EDUCATION
                if "-" in subject_info[10]
                else config_data.HtmlContent_NUMBER_EDUCATION
            ),
            subject_info[10],
        )
        if subject_info[10] != "-"
        else "<div class='info-number-education-error'><span class='label'>"
        + config_data.InformationMessages_LEVEL_NOT_DEFINED
        + "</span></div>"
    )

    return "".join(
        [
            create_html_block(config_data.HtmlContent_SUBJECT_LABEL, subject_info[1]),
            create_html_block(
                config_data.HtmlContent_ID_SUBJECT_LABEL, subject_info[0]
            ),
            create_html_block(
                config_data.HtmlContent_DEPARTMENT_LABEL, subject_info[5]
            ),
            create_html_block(config_data.HtmlContent_FACULTY_LABEL, subject_info[4]),
            create_html_block(config_data.HtmlContent_CAMPUS_LABEL, subject_info[3]),
            create_html_block(edu_level_label, edu_level),
            number_education_block,
            create_html_block(config_data.HtmlContent_AUDIENCE_LABEL, subject_info[8]),
            create_html_block(config_data.HtmlContent_FORMAT_LABEL, subject_info[9]),
        ]
    )


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

    vacancy_embedding = get_embeddings(message, model_manager_sbert.get_current_model())

    with torch.no_grad():
        similarities = (
            cosine_similarity(
                vacancy_embedding, model_manager_sbert.state.puds_embeddings
            )
            .cpu()
            .tolist()
        )
        similarities = [
            (i, j)
            for i, j in zip(
                model_manager_sbert.state.puds_names["names"].to_list(), similarities
            )
        ]

    sorted_subjects = sorted(similarities, key=lambda x: x[1], reverse=True)
    unique_subjects = filter_unique_items(sorted_subjects, top_subjects)

    all_top_items = []

    for subject, similarity in unique_subjects:
        match = next(
            (
                item
                for item in model_manager_sbert.get_puds_data()
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
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[7], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[8], "-")}"
            )
        else:
            formatted_subject = f"- | {subject} | CS={similarity:.4f}"

        all_top_items.append(formatted_subject)

    subjects_sorted = sort_subjects(all_top_items)

    grouped_subjects = {}
    for subject in subjects_sorted.split(";"):
        subject_info = list(map(str.strip, subject.split("|")))

        edu_level_label, edu_level = determine_edu_level(subject_info)

        if edu_level not in grouped_subjects:
            grouped_subjects[edu_level] = []
        grouped_subjects[edu_level].append((subject_info, edu_level_label, edu_level))

    content = ""
    for edu_level, subjects in grouped_subjects.items():
        content += (
            f"<div class='edu-group'><span>{edu_level}</span><div class='subject-info'>"
        )

        content += "".join(
            "<div class='info'>"
            + generate_subject_info(subject_info, edu_level_label, edu_level)
            + generate_skills(subject_info[0], max_skill_words)
            + "</div>"
            for subject_info, edu_level_label, edu_level in subjects
        )

        content += "</div></div>"

    chat_history.append(ChatMessage(role="user", content=message))
    chat_history.append(ChatMessage(role="assistant", content=content))

    return (gr.Textbox(value=None), chat_history)
