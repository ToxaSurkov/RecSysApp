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
    path: str, drop_duplicates: bool = False, subset: Optional[list[str]] = None
) -> pl.DataFrame:
    df = pl.read_parquet(Path(path))

    if drop_duplicates and subset:
        df = df.unique(subset=subset, keep="first", maintain_order=False)

    return df


def load_puds_data(
    path: str,
    year: str,
    drop_duplicates: bool = False,
    subset: Optional[list[str]] = None,
    full_info_cols: Optional[list[str]] = None,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    df = pl.read_parquet(Path(path))

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
    force_reload: bool = False,
) -> tuple[torch.Tensor, pl.DataFrame]:
    embeddings_col = "embeddings"
    names_col = "names"
    subject_info_col = config_data.DataframeHeaders_SUBJECTS_FULL_INFO
    subject_name_col = config_data.DataframeHeaders_RU_SUBJECTS[0]

    embeddings_path = Path(config_data.StaticPaths_PUDS_EMBEDDINGS)
    names_path = Path(config_data.StaticPaths_RU_SUBJECTS)

    def load_existing_data() -> tuple[torch.Tensor, pl.DataFrame]:
        embeddings = load_file(embeddings_path)[embeddings_col]
        names = pl.read_parquet(names_path)

        return embeddings, names

    def save_embeddings(embeddings: torch.Tensor, names: list[str]) -> None:
        if embeddings.size(0) > 0:
            save_file({embeddings_col: embeddings}, embeddings_path)
        if names:
            pl.DataFrame({names_col: names}).write_parquet(names_path)

    def valid_cached_data(embeddings: torch.Tensor, names: pl.DataFrame) -> bool:
        return embeddings.size(0) == names.shape[0] > 0

    if not force_reload and embeddings_path.is_file() and names_path.is_file():
        embeddings, names = load_existing_data()

        if valid_cached_data(embeddings, names):
            if limit:
                return embeddings[:limit], names[:limit]

            return embeddings, names

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

    embeddings_tensor = torch.stack(embeddings) if embeddings else torch.Tensor()

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


def extract_numbers(value):
    numbers = re.findall(r"(\d+)\s*модуль", value)
    return [int(num) for num in numbers] if numbers else None


def custom_sort_key(r: str) -> tuple[int, float, float]:
    l = r.strip().split("|")

    category = l[6].strip() if len(l) > 6 else "nan"

    edu_priority = {
        item: index for index, item in enumerate(config_data.Settings_PRIORITY)
    }

    category_priority = edu_priority.get(category, edu_priority["nan"])

    numbers = extract_numbers(l[7].strip()) if len(l) > 7 else []

    first_module = numbers[0] if numbers else float("inf")
    last_module = numbers[-1] if numbers else float("inf")

    return category_priority, first_module, last_module


def sort_subjects(subjects):
    subjects = [d.strip() for d in subjects.split(";")]

    sorted_subjects = sorted(subjects, key=custom_sort_key)

    return "; ".join(sorted_subjects)
