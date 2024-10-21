"""
File: login.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to settings.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_init import model_manager_sbert


def event_handler_dropdown_models(message: str, dropdown_models: str) -> gr.Button:
    with model_manager_sbert.switch_model(dropdown_models):
        gr.Info(config_data.AppInfo_MODEL.format(dropdown_models))

        message = message.strip()

        return gr.Button(interactive=bool(message))
