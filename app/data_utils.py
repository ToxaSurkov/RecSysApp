"""
File: utils.py
Author: Dmitry Ryumin
Description: Functions for data handling.
License: MIT License
"""

import re
import torch
import polars as pl
from pathlib import Path, PosixPath
from typing import Union, Optional

from sentence_transformers import SentenceTransformer
from safetensors.torch import save_file, load_file

# Importing necessary components for the Gradio app
from app.gpu_init import device
from app.config import config_data


def get_files(directory: Union[str, Path], ext: str = "parquet") -> list[Path]:
    def custom_sort_key(file_name: Path) -> tuple:
        name = file_name.stem

        match name:
            case _ if re.match(r"^[A-Za-z]", name):
                return (1, name)
            case _ if re.match(r"^[А-Яа-яЁё]", name):
                return (2, name)
            case _ if re.match(r"^\d", name):
                return (3, name)
            case _:
                return (4, name)

    path2files = Path(directory)
    files = list(path2files.rglob(f"*.{ext}"))

    sorted_files = sorted(files, key=custom_sort_key)

    return sorted_files


def load_parquet(
    path: PosixPath, drop_duplicates: bool = False, subset: Optional[list[str]] = None
) -> pl.DataFrame:
    df = pl.read_parquet(path)

    if drop_duplicates and subset:
        df = df.unique(subset=subset, keep="first", maintain_order=False)

    return df


def load_puds_data(
    path: PosixPath,
    year: str,
    drop_duplicates: bool = False,
    subset: Optional[list[str]] = None,
    full_info_cols: Optional[list[str]] = None,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    df = pl.read_parquet(path)

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
        embeddings = sbert_model.encode(
            text,
            task=config_data.Models_TASK,
            convert_to_tensor=True,
            device=device,
        )

    return embeddings


def extract_embeddings(
    model_name: str,
    d_puds_cleaned: list[dict],
    sbert_model: SentenceTransformer,
    limit: Optional[int] = None,
    force_reload: bool = False,
) -> tuple[torch.Tensor, pl.DataFrame]:
    names_col = "names"
    subject_info_col = config_data.DataframeHeaders_SUBJECTS_FULL_INFO
    subject_name_col = config_data.DataframeHeaders_RU_SUBJECTS[0]

    embeddings_path = config_data.Path_APP / config_data.StaticPaths_PUDS_EMBEDDINGS
    names_path = config_data.Path_APP / config_data.StaticPaths_RU_SUBJECTS

    embeddings_path = (
        embeddings_path.parent
        / f"{embeddings_path.stem}_{model_name}{embeddings_path.suffix}"
    )

    names_path = (
        names_path.parent / f"{names_path.stem}_{model_name}{names_path.suffix}"
    )

    def load_existing_data() -> tuple[torch.Tensor, pl.DataFrame]:
        embeddings = load_file(embeddings_path)[config_data.Models_EMBEDDINGS_NAME]
        names = pl.read_parquet(names_path)

        return embeddings, names

    def save_embeddings(embeddings: torch.Tensor, names: list[str]) -> None:
        if embeddings.size(0) > 0:
            save_file({config_data.Models_EMBEDDINGS_NAME: embeddings}, embeddings_path)
        if names:
            pl.DataFrame({names_col: names}).write_parquet(names_path)

    def valid_cached_data(embeddings: torch.Tensor, names: pl.DataFrame) -> bool:
        return embeddings.size(0) == names.shape[0] > 0

    if not force_reload and embeddings_path.is_file() and names_path.is_file():
        embeddings, names = load_existing_data()

        if valid_cached_data(embeddings, names):
            if limit:
                return embeddings[:limit], names[:limit]

            return embeddings.to(sbert_model.device), names

    def process_item(item: dict) -> tuple[Optional[torch.Tensor], Optional[str]]:
        subject_info = item.get(subject_info_col)
        subject_name = item.get(subject_name_col)

        if subject_info:
            return get_embeddings(subject_info, sbert_model), subject_name

        return None, None

    processed_items = [
        process_item(item)
        for item in (d_puds_cleaned[:limit] if limit else d_puds_cleaned)
    ]

    embeddings, names = zip(
        *(
            (embedding, name)
            for embedding, name in processed_items
            if embedding is not None and name is not None
        )
    )

    embeddings_tensor = (
        torch.stack(embeddings).to(sbert_model.device) if embeddings else torch.Tensor()
    )

    save_embeddings(embeddings_tensor, list(names))

    return embeddings_tensor, pl.DataFrame({names_col: list(names)})


def filter_unique_items(
    sorted_items: list[tuple[str, float]], top_n: int
) -> list[tuple[str, float]]:
    unique_items = []
    seen_items = set()

    for item, similarity in sorted_items:
        if item not in seen_items:
            seen_items.add(item)
            unique_items.append((item, similarity))
        if len(unique_items) >= top_n:
            break

    return unique_items


def extract_numbers(courses_str: str) -> list[int]:
    return [int(num) for num in re.findall(r"\d+", courses_str)]


def sort_courses(courses: str, edu_level: str) -> Optional[list[int]]:
    course_pairs = re.findall(
        r"({})\s*,\s*(\d)\s*курс".format(
            config_data.EducationLevels_ALL_LEVELS.replace(", ", "|")
        ),
        courses,
    )

    all_levels = config_data.EducationLevels_ALL_LEVELS.split(", ")

    valid_courses = [
        int(year)
        for level, year in course_pairs
        if level == edu_level
        and int(year)
        in {
            all_levels[0]: range(1, 5),
            all_levels[1]: {1},
            all_levels[2]: range(1, 3),
            all_levels[3]: range(1, 4),
        }[level]
    ]

    return valid_courses


def sort_subjects(subjects: list[str]) -> str:
    grouped_subjects = {}

    for subject in subjects:
        parts = subject.split("|")

        level = parts[6].strip()
        courses_str = parts[10].strip()

        if courses_str.lower() == config_data.EducationLevels_NONE_LEVELS.lower():
            sorted_courses = []
        else:
            sorted_courses = sort_courses(courses_str, level)

        if level not in grouped_subjects:
            grouped_subjects[level] = []

        grouped_subjects[level].append((sorted_courses, subject))

    result = []

    for level in sorted(
        grouped_subjects.keys(),
        key=lambda x: (
            config_data.Settings_PRIORITY.index(x)
            if x in config_data.Settings_PRIORITY
            else float("inf")
        ),
    ):
        items = grouped_subjects[level]

        sorted_items = sorted(
            items, key=lambda x: (min(x[0]) if x[0] else float("inf"), len(x[0]))
        )

        for courses, item in sorted_items:
            parts = item.split("|")

            if courses:
                if len(courses) > 1:
                    courses = sorted(courses)

                    compact_courses = f"{courses[0]}-{courses[-1]}"
                else:
                    compact_courses = str(courses[0])
            else:
                compact_courses = None

            parts[10] = compact_courses if compact_courses else None

            result.append(
                " | ".join(part.strip() if part is not None else "-" for part in parts)
            )

    return "; ".join(result)
