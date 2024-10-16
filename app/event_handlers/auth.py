"""
File: auth.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to change auth.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data
from app.components import html_message


def event_handler_auth(
    surname: str, username: str, dropdown_user: str
) -> tuple[gr.Button, gr.HTML]:
    surname = surname.strip()
    username = username.strip()

    is_auth_valid = (
        surname
        and username
        and dropdown_user
        and dropdown_user != config_data.Settings_DROPDOWN_USER[0]
    )

    return (
        gr.Button(
            value=config_data.OtherMessages_AUTH,
            interactive=is_auth_valid,
            scale=1,
            icon=config_data.StaticPaths_IMAGES + "auth.ico",
            visible=True,
            elem_classes="auth",
        ),
        html_message(
            message=config_data.InformationMessages_NOTI_AUTH[
                1 if is_auth_valid else 0
            ],
            error=not is_auth_valid,
            visible=True,
        ),
    )
