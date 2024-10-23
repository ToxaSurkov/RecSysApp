"""
File: app.py
Author: Dmitry Ryumin
Description: Main application file.
             The file defines the Gradio interface, sets up the main blocks and tabs,
             and includes event handlers for various components.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import CONFIG_NAME, config_data, load_tab_creators
from app.event_handlers.event_handlers import setup_app_event_handlers
import app.tabs


gr.set_static_paths(paths=[config_data.Path_APP / config_data.StaticPaths_IMAGES])


def create_gradio_app() -> gr.Blocks:
    with gr.Blocks(
        theme=gr.themes.Default(), css_paths=config_data.AppSettings_CSS_PATH
    ) as gradio_app:
        tab_results = {}

        available_functions = {
            attr: getattr(app.tabs, attr)
            for attr in dir(app.tabs)
            if callable(getattr(app.tabs, attr)) and attr.endswith("_tab")
        }

        tab_creators = load_tab_creators(CONFIG_NAME, available_functions)

        for tab_name, create_tab_function in tab_creators.items():
            with gr.Tab(tab_name):
                app_instance = create_tab_function()
                tab_results[tab_name] = app_instance

        keys = list(tab_results.keys())

        setup_app_event_handlers(*(tab_results[keys[0]] + tab_results[keys[1]]))

    return gradio_app


if __name__ == "__main__":
    create_gradio_app().queue(api_open=False).launch(server_name="0.0.0.0", share=False)
