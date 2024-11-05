"""
File: tabs.py
Author: Dmitry Ryumin
Description: Gradio app tabs - Contains the definition of various tabs for the Gradio app interface.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.description import DESCRIPTION
from app.description_steps import STEP_1, STEP_2
from app.config import config_data
from app.requirements_app import read_requirements
from app.components import html_message


def app_tab():
    gr.Markdown(value=DESCRIPTION)

    gr.HTML(value=STEP_1)

    with gr.Row(
        visible=True,
        render=True,
        variant="default",
        elem_classes="user-container",
    ):
        surname = gr.Textbox(
            value=None,
            lines=1,
            max_lines=1,
            placeholder=config_data.OtherMessages_IMPORTANT,
            label=config_data.Labels_SURNAME,
            info=config_data.InformationMessages_SURNAME,
            show_label=True,
            container=True,
            scale=1,
            interactive=True,
            visible=True,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=config_data.Settings_USER_MAX_LENGTH,
            elem_classes="user-info",
        )

        username = gr.Textbox(
            value=None,
            lines=1,
            max_lines=1,
            placeholder=config_data.OtherMessages_IMPORTANT,
            label=config_data.Labels_USERNAME,
            info=config_data.InformationMessages_USERNAME,
            show_label=True,
            container=True,
            scale=1,
            interactive=True,
            visible=True,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=config_data.Settings_USER_MAX_LENGTH,
            elem_classes="user-info",
        )

        dropdown_user = gr.Dropdown(
            choices=config_data.Settings_DROPDOWN_USER,
            value=None,
            multiselect=False,
            allow_custom_value=False,
            label=config_data.Labels_USER_AFFILIATION,
            info=config_data.InformationMessages_USER_AFFILIATION,
            show_label=True,
            interactive=True,
            visible=True,
            render=True,
            elem_classes="dropdown-user",
        )

    with gr.Row(
        visible=True,
        render=True,
        variant="default",
        elem_classes="auth-container",
    ):
        auth = gr.Button(
            value=config_data.OtherMessages_AUTH,
            interactive=False,
            scale=1,
            icon=config_data.Path_APP / config_data.StaticPaths_IMAGES / "auth.ico",
            visible=True,
            elem_classes="auth",
        )

    noti_auth = html_message(
        message=config_data.InformationMessages_NOTI_AUTH[0],
        error=True,
        visible=True,
    )

    step_2 = gr.HTML(value=STEP_2, visible=False)

    with gr.Column(
        visible=False,
        render=True,
        variant="default",
        elem_classes="chatbot-container",
    ) as chatbot_column:
        chatbot = gr.Chatbot(
            type="messages",
            label=config_data.Labels_CHATBOT,
            autoscroll=False,
            visible=False,
            render=True,
            show_copy_button=True,
            avatar_images=(
                config_data.Path_APP / config_data.StaticPaths_IMAGES / "user.svg",
                config_data.Path_APP / config_data.StaticPaths_IMAGES / "HSE.svg",
            ),
            elem_classes="chatbot",
        )

        with gr.Row(
            visible=False,
            render=True,
            variant="default",
            elem_classes="message-container",
        ) as message_row:
            message = gr.Textbox(
                value=None,
                lines=1,
                max_lines=20,
                placeholder=config_data.OtherMessages_JOB_DESC,
                label=None,
                info=None,
                show_label=False,
                container=False,
                scale=7,
                interactive=True,
                visible=False,
                autofocus=False,
                autoscroll=True,
                render=True,
                type="text",
                show_copy_button=True,
                max_length=None,
            )

            send_message = gr.Button(
                value="",
                interactive=False,
                scale=1,
                icon=config_data.Path_APP
                / config_data.StaticPaths_IMAGES
                / "btn_message.svg",
                visible=False,
                elem_classes="send_message",
            )

    return (
        surname,
        username,
        dropdown_user,
        auth,
        noti_auth,
        step_2,
        chatbot_column,
        chatbot,
        message_row,
        message,
        send_message,
    )


def settings_app_tab():
    with gr.Row(
        visible=True,
        render=True,
        variant="default",
        elem_classes="settings-container",
    ):
        top_subjects = gr.Number(
            value=config_data.Settings_TOP_SUBJECTS,
            label=config_data.Labels_TOP_SUBJECTS,
            info=config_data.InformationMessages_FROM_TO.format(
                config_data.Settings_TOP_SUBJECTS_RANGE[0],
                config_data.Settings_TOP_SUBJECTS_RANGE[1],
            ),
            show_label=True,
            container=True,
            scale=1,
            interactive=True,
            visible=True,
            render=True,
            minimum=config_data.Settings_TOP_SUBJECTS_RANGE[0],
            maximum=config_data.Settings_TOP_SUBJECTS_RANGE[1],
            step=1,
            elem_classes="settings-item",
        )

        max_skill_words = gr.Number(
            value=config_data.Settings_MAX_SKILL_WORDS,
            label=config_data.Labels_MAX_SKILL_WORDS,
            info=config_data.InformationMessages_FROM_TO.format(
                config_data.Settings_MAX_SKILL_WORDS_RANGE[0],
                config_data.Settings_MAX_SKILL_WORDS_RANGE[1],
            ),
            show_label=True,
            container=True,
            scale=1,
            interactive=True,
            visible=True,
            render=True,
            minimum=config_data.Settings_MAX_SKILL_WORDS_RANGE[0],
            maximum=config_data.Settings_MAX_SKILL_WORDS_RANGE[1],
            step=1,
            elem_classes="settings-item",
        )

        dropdown_models = gr.Dropdown(
            choices=config_data.Models_SBERT,
            value=config_data.Models_SBERT[0],
            multiselect=False,
            allow_custom_value=False,
            label=config_data.Labels_MODEL,
            info=config_data.InformationMessages_MODEL,
            show_label=True,
            interactive=True,
            visible=True,
            render=True,
            elem_classes="dropdown-models",
        )

    return (top_subjects, max_skill_words, dropdown_models)


# def about_app_tab():
#     pass


# def about_authors_tab():
#     pass


def requirements_app_tab():
    reqs = read_requirements()

    return gr.Dataframe(
        headers=reqs.columns,
        value=reqs,
        datatype=["markdown"] * len(reqs.columns),
        visible=True,
        elem_classes="requirements-dataframe",
        type="polars",
    )
