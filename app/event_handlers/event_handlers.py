"""
File: event_handlers.py
Author: Dmitry Ryumin
Description: File containing functions for configuring event handlers for Gradio components.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.event_handlers.auth import event_handler_auth
from app.event_handlers.login import event_handler_login
from app.event_handlers.generate_response import event_handler_generate_response
from app.event_handlers.message import event_handler_message


def setup_app_event_handlers(
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
    top_subjects,
    max_skill_words,
    dropdown_models,
):
    gr.on(
        triggers=[surname.change, username.change, dropdown_user.change],
        fn=event_handler_auth,
        inputs=[surname, username, dropdown_user],
        outputs=[
            auth,
            noti_auth,
        ],
        queue=True,
    )

    auth.click(
        fn=event_handler_login,
        inputs=[surname, username, dropdown_user],
        outputs=[
            surname,
            username,
            dropdown_user,
            auth,
            noti_auth,
            step_2,
            message_row,
            chatbot_column,
            chatbot,
            message,
            send_message,
        ],
        queue=True,
    )

    message.change(
        fn=event_handler_message,
        inputs=[message],
        outputs=[send_message],
        queue=True,
    )

    gr.on(
        triggers=[message.submit, send_message.click],
        fn=event_handler_generate_response,
        inputs=[
            message,
            chatbot,
            top_subjects,
            max_skill_words,
        ],
        outputs=[message, chatbot],
        queue=True,
    )
