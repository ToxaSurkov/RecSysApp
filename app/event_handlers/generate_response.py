"""
File: login.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to generate response.
License: MIT License
"""

import torch
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
)
from app.data_utils import get_embeddings, filter_unique_items, sort_subjects


def event_handler_generate_response(
    message: str, chat_history: list[ChatMessage]
) -> tuple[gr.Textbox, list[ChatMessage]]:
    message = message.strip()

    if message:
        vacancy_embedding = get_embeddings(message, sbert_model)

        with torch.no_grad():
            similarities = (
                cosine_similarity(vacancy_embedding, puds_embeddings).cpu().tolist()
            )
            similarities = [(i, j) for i, j in zip(puds_names, similarities)]

        sorted_subjects = sorted(similarities, key=lambda x: x[1], reverse=True)
        unique_subjects = filter_unique_items(
            sorted_subjects, config_data.Settings_TOP_SUBJECTS
        )

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
                subject_id = match.get("ID дисциплины БУП ППК (АСАВ)", "-")
                campus = match.get("Кампус кафедры, предлагающей дисциплину", "-")
                faculty = match.get("Факультет кафедры, предлагающей дисциплину", "-")
                department = match.get("Кафедра, предлагающая дисциплину", "-")
                level = match.get("Уровень обучения", "-")
                period = match.get("Период изучения дисциплины", "-")
                coverage = match.get("Охват аудитории", "-")
                form = match.get("Формат изучения", "-")

                formatted_subject = (
                    f"{subject_id} | {subject} | CS={similarity:.4f} | {campus} | {faculty} | "
                    + f"{department} | {level} | {period} | {coverage} | {form}"
                )
                all_top_items.append(formatted_subject)
            else:
                all_top_items.append(f"- | {subject} | CS={similarity:.4f}")

        subjects_sorted = sort_subjects("; ".join(all_top_items))

        content = "<div class='subject-info'>"

        for subject in subjects_sorted.split(";"):
            subject_info = subject.split("|")

            content += (
                "<div class='info'>"
                + "<div class='info-item'><span class='label'>Дисциплина:</span> <span class='value'>"
                + subject_info[1].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>ID дисциплины:</span> <span class='value'>"
                + subject_info[0].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>Кафедра:</span> <span class='value'>"
                + subject_info[5].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>Факультет кафедры:</span> <span class='value'>"
                + subject_info[4].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>Кампус:</span> <span class='value'>"
                + subject_info[3].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>Уровень обучения:</span> <span class='value'>"
                + subject_info[6].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>Охват аудитории:</span> <span class='value'>"
                + subject_info[8].strip()
                + "</span></div>"
                + "<div class='info-item'><span class='label'>Формат изучения:</span> <span class='value'>"
                + subject_info[9].strip()
                + "</span></div>"
                + "</div>"
            )

        content += "</div>"

        chat_history.append(ChatMessage(role="user", content=message))
        chat_history.append(ChatMessage(role="assistant", content=content))

    return (gr.Textbox(value=None), chat_history)
