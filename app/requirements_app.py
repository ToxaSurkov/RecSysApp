"""
File: requirements_app.py
Author: Dmitry Ryumin
Description: Project requirements for the Gradio app.
License: MIT License
"""

import polars as pl

# Importing necessary components for the Gradio app


def read_requirements(file_path="requirements.txt"):
    with open(file_path, "r") as file:
        lines = file.readlines()

    data = []

    pypi = (
        lambda x: f"<a href='https://pypi.org/project/{x}' target='_blank'>"
        + f"<img src='https://img.shields.io/pypi/v/{x}' alt='PyPI' /></a>"
    )

    data = [
        {
            "Библиотека": split_line[0],
            "Рекомендованная версия": split_line[1],
            "Текущая версия": pypi(split_line[0]),
        }
        for line in lines
        if (split_line := line.strip().split("==")) and len(split_line) == 2
    ]

    df = pl.DataFrame(data)

    return df
