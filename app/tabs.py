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
        )

        dropdown_user = gr.Dropdown(
            choices=config_data.Settings_DROPDOWN_USER,
            value=config_data.Settings_DROPDOWN_USER[0],
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
            icon=config_data.StaticPaths_IMAGES + "auth.ico",
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
                config_data.StaticPaths_IMAGES + "user.svg",
                config_data.StaticPaths_IMAGES + "HSE.svg",
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
                icon=config_data.StaticPaths_IMAGES + "message.svg",
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


def about_app_tab():
    pass


def about_authors_tab():
    pass


def requirements_app_tab():
    pass
