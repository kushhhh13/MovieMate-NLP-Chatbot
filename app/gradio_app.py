"""
Gradio chat interface with poster thumbnails.

This reuses the exact same MovieChatBot, MovieRetriever, and LLM generation
step that app/main.py (the FastAPI service) uses, it's a demo front end,
not a second implementation of the chatbot logic.

build_demo(retriever) is the reusable piece: app/main.py imports this and
mounts it directly onto the deployed FastAPI app at /ui, so the live
Render deployment has an actual visual chat interface, not just a JSON
API. Running this file standalone (python -m app.gradio_app) still works
too, for local-only use, it just builds its own retriever first.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

import gradio as gr

from .chatbot import MovieChatBot


def _poster_html(results) -> str:
    """Builds small inline poster thumbnails from the current turn's
    retrieved movies. Kept out of the LLM prompt entirely, the model never
    sees or repeats these URLs, they're attached to the reply afterward."""
    if results is None or results.empty:
        return ""

    thumbs = []
    for _, row in results.iterrows():
        poster = row.get("Poster_Link")
        if isinstance(poster, str) and poster.startswith("http"):
            title = row["Series_Title"]
            thumbs.append(
                f'<img src="{poster}" alt="{title}" title="{title}" '
                f'width="90" style="display:inline-block;margin:4px;'
                f'border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,0.3);">'
            )
    return "<div>" + "".join(thumbs) + "</div>" if thumbs else ""


def build_demo(retriever) -> gr.Blocks:
    def respond(user_message, history, bot_state):
        bot = bot_state or MovieChatBot(retriever)

        try:
            reply = bot.chat(user_message)
        except RuntimeError as e:
            reply = f"\u26a0\ufe0f {e}"

        posters = _poster_html(bot.last_results)
        full_reply = reply + ("\n\n" + posters if posters else "")

        history = history + [[user_message, full_reply]]
        return "", history, bot

    with gr.Blocks(title="MovieMate") as demo:
        gr.Markdown(
            """
            # \U0001F3AC MovieMate
            **Your personal IMDb movie recommendation assistant**, backed by
            real retrieval-augmented generation (TF-IDF + FAISS retrieval, an
            LLM via Groq for the reply) with poster thumbnails.

            Try asking:
            - *"Suggest thriller movies after 2000"*
            - *"Best comedy movies from the 1990s"*
            - *"Movies directed by Christopher Nolan"*
            - *"Highly rated crime movies under 2 hours"*
            """
        )

        chatbot_ui = gr.Chatbot(height=500, label="MovieMate Chat")
        bot_state = gr.State(None)

        with gr.Row():
            input_box = gr.Textbox(
                placeholder="Ask me about movies...", label="Your message", scale=8
            )
            send_btn = gr.Button("Send \U0001F3AC", scale=1, variant="primary")

        clear_btn = gr.Button("Clear Chat")

        send_btn.click(
            fn=respond,
            inputs=[input_box, chatbot_ui, bot_state],
            outputs=[input_box, chatbot_ui, bot_state],
        )
        input_box.submit(
            fn=respond,
            inputs=[input_box, chatbot_ui, bot_state],
            outputs=[input_box, chatbot_ui, bot_state],
        )
        clear_btn.click(
            lambda: ([], "", None),
            outputs=[chatbot_ui, input_box, bot_state],
        )

    return demo


if __name__ == "__main__":
    from .data_prep import load_and_clean_data
    from .retrieval import MovieRetriever

    _df = load_and_clean_data(os.environ.get("MOVIE_CSV_PATH", "IMDB_Top_1000_Movies.csv"))
    _retriever = MovieRetriever(_df)
    build_demo(_retriever).launch()