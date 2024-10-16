"""
File: utils.py
Author: Dmitry Ryumin
Description: Functions for data handling.
License: MIT License
"""

import re
import torch
import polars as pl
from pathlib import Path
from typing import Union, Optional

from sentence_transformers import SentenceTransformer

# Importing necessary components for the Gradio app
from app.gpu_init import device
from app.config import config_data


def get_files(directory: Union[str, Path], ext: str = "parquet") -> list[Path]:
    def custom_sort_key(file_name: Path) -> tuple:
        name = file_name.stem

        # Классификация: 1 для английских, 2 для русских, 3 для цифр
        match name:
            case _ if re.match(r"^[A-Za-z]", name):  # Английские буквы
                return (1, name)
            case _ if re.match(r"^[А-Яа-яЁё]", name):  # Русские буквы
                return (2, name)
            case _ if re.match(r"^\d", name):  # Цифры
                return (3, name)
            case _:
                return (4, name)  # Все остальные символы

    path2files = Path(directory)
    files = list(path2files.rglob(f"*.{ext}"))

    # Сортировка по кастомному ключу
    sorted_files = sorted(files, key=custom_sort_key)

    return sorted_files


def load_puds_data(
    directory: str,
    year: str,
    drop_duplicates: bool = False,
    subset: Optional[list[str]] = None,
    full_info_cols: Optional[list[str]] = None,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    df = pl.read_parquet(Path(directory))

    alias_year = "year"

    df = df.with_columns(
        pl.col(year)
        .fill_null("")
        .cast(pl.Utf8)
        .str.extract(r"(\d{4}/\d{4})", 0)
        .fill_null("0000/0000")
        .alias(alias_year)
    )

    df = df.sort(
        by=[subset[0], alias_year],
        descending=[False, True],
        multithreaded=True,
        maintain_order=False,
    )

    if drop_duplicates and subset:
        df = df.unique(subset=subset, keep="first", maintain_order=False)

    if full_info_cols:
        alias_full_info = config_data.DataframeHeaders_SUBJECTS_FULL_INFO

        df = df.with_columns(
            pl.concat_str(
                [
                    pl.col(subset[0]),
                    pl.lit("\nАннотация: "),
                    pl.col(full_info_cols[0]).fill_null(""),
                    pl.lit("\nСписок разделов: "),
                    pl.col(full_info_cols[1]).fill_null(""),
                    pl.lit("\nСписок планируемых результатов обучения: "),
                    pl.col(full_info_cols[2]).fill_null(""),
                ]
            ).alias(alias_full_info)
        )

        df_grouped = df.group_by(subset[1]).agg(
            pl.col(alias_full_info).alias("full_info_list")
        )
    else:
        df_grouped = pl.DataFrame({})

    return df, df_grouped


def get_embeddings(text: str, sbert_model: SentenceTransformer) -> torch.Tensor:
    with torch.no_grad():
        embeddings = sbert_model.encode(text, convert_to_tensor=True, device=device)

    return embeddings


def extract_embeddings(
    d_puds_cleaned: list[dict],
    sbert_model: SentenceTransformer,
    limit: Optional[int] = None,
) -> tuple[list, list]:
    embeddings = []
    names = []

    items_to_process = d_puds_cleaned[:limit] if limit else d_puds_cleaned

    def process_item(item):
        subject_name = item.get(config_data.DataframeHeaders_RU_SUBJECTS[0])
        subject_full_info = item.get(config_data.DataframeHeaders_SUBJECTS_FULL_INFO)

        if subject_full_info:
            subject_embedding = get_embeddings(subject_full_info, sbert_model)
            return subject_embedding, subject_name

        return None, None

    items = [process_item(item) for item in items_to_process]

    for embedding, name in items:
        if embedding is not None and name is not None:
            embeddings.append(embedding)
            names.append(name)

    if embeddings:
        embeddings = torch.stack(embeddings)
    else:
        embeddings = torch.Tensor()

    return embeddings, names


def filter_unique_items(sorted_items: list, top_n: int) -> list:
    unique_items = []
    seen_items = set()

    for item, similarity in sorted_items:
        if item not in seen_items:
            seen_items.add(item)
            unique_items.append((item, similarity))
            if len(unique_items) >= top_n:
                break

    if len(unique_items) < top_n:
        for item, similarity in sorted_items[len(unique_items) :]:
            if item not in seen_items:
                seen_items.add(item)
                unique_items.append((item, similarity))
                if len(unique_items) >= top_n:
                    break

    return unique_items


def extract_numbers(value):
    numbers = re.findall(r"(\d+)\s*модуль", value)
    return [int(num) for num in numbers] if numbers else None


def custom_sort_key(r):
    l = r.strip().split("|")

    category = l[6].strip() if len(l) > 6 else "nan"

    edu_priority = {
        item: index for index, item in enumerate(config_data.Settings_PRIORITY)
    }

    category_priority = edu_priority.get(category, edu_priority["nan"])

    numbers = extract_numbers(l[7].strip()) if len(l) > 7 else None
    if numbers is None:
        first_module, last_module = float("inf"), float("inf")
    else:
        first_module = numbers[0]
        last_module = numbers[-1]

    return (category_priority, first_module, last_module)


def sort_subjects(subjects):
    subjects = [d.strip() for d in subjects.split(";")]

    sorted_subjects = sorted(subjects, key=custom_sort_key)

    return "; ".join(sorted_subjects)
