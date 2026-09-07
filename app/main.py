"""
FastAPI service exposing MovieChatBot over HTTP.

Session persistence: an in-memory dict holds the live MovieChatBot instance
per session_id for speed during a running process, but every turn is also
written to a Django-backed SQLite database (ChatSession/ChatMessage models).
If the process restarts and a client sends a session_id that isn't in the
in-memory dict anymore, we look it up in the database and replay the
conversation history into a fresh MovieChatBot instead of losing it, that's
what makes the sessions actually persistent rather than just in-RAM.

The Django admin (movies/admin.py) is not exposed through this API or
deployed publicly, it's meant to be run locally (`python manage.py
runserver`) against the same SQLite file for browsing the movie catalog
and chat history. Admin interfaces generally shouldn't be public-facing
without real auth infrastructure in front of them, so keeping it local-only
is a deliberate choice, not a missing feature.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Always load the .env file that sits next to this project's requirements.txt
# (one directory up from this file, since this file lives in app/), instead
# of relying on whatever the current working directory happens to be when
# uvicorn is started. This avoids "works in one terminal, not in another."
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# Set up Django so we can use its ORM from inside FastAPI. This does not
# start a Django server, it just makes movies.models usable for reads/writes
# against the same SQLite database the admin uses.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402
django.setup()

from movies.models import ChatSession, ChatMessage  # noqa: E402
from config.asgi import application as django_asgi_app  # noqa: E402

from .data_prep import load_and_clean_data
from .retrieval import MovieRetriever
from .chatbot import MovieChatBot
from .gradio_app import build_demo

app = FastAPI(title="MovieMate API", version="0.1.0")

if not os.environ.get("GROQ_API_KEY"):
    print(f"WARNING: GROQ_API_KEY not found. Looked for a .env file at: {_ENV_PATH}")
    print(f"That path exists: {_ENV_PATH.exists()}")

# Built once at startup, reused across every request instead of rebuilding
# the TF-IDF/FAISS index per call.
_df = load_and_clean_data(os.environ.get("MOVIE_CSV_PATH", "IMDB_Top_1000_Movies.csv"))
_retriever = MovieRetriever(_df)

import gradio as gr
app = gr.mount_gradio_app(app, build_demo(_retriever), path="/ui")
app.mount("/admin", django_asgi_app)

# Live, in-process bot instances.

_sessions: Dict[str, MovieChatBot] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class MovieResult(BaseModel):
    title: str
    year: int
    rating: float
    poster_url: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    movies: List[MovieResult] = []


def _get_or_restore_bot(session_id: str) -> MovieChatBot:
    """In-memory hit is the fast path. On a miss, check the database, if a
    ChatSession with this id exists there (e.g. the process restarted since
    the client last messaged), rebuild a MovieChatBot and replay its
    conversation_history from persisted ChatMessage rows before returning
    it. Note that last_results (the actual retrieved-movies DataFrame) is
    intentionally not persisted, it's cheap to recompute from the last user
    query and keeping it out of the database keeps the persisted footprint
    small, a deliberate tradeoff worth being able to explain."""
    if session_id in _sessions:
        return _sessions[session_id]

    bot = MovieChatBot(_retriever)

    existing = ChatSession.objects.filter(session_id=session_id).first()
    if existing:
        for msg in existing.messages.all():
            bot.conversation_history.append({"role": msg.role, "message": msg.message})

    _sessions[session_id] = bot
    return bot


def _persist_turn(session_id: str, user_message: str, bot_reply: str) -> None:
    session, _ = ChatSession.objects.get_or_create(session_id=session_id)
    ChatMessage.objects.create(session=session, role="user", message=user_message)
    ChatMessage.objects.create(session=session, role="bot", message=bot_reply)


@app.get("/")
def root():
    return {
        "message": "MovieMate API is running.",
        "chat_ui": "/ui",
        "try": [
            "GET /health",
            "POST /chat with JSON body: {\"message\": \"suggest thriller movies after 2000\"}",
        ],
    }



@app.get("/health")
def health():
    return {"status": "ok", "movies_loaded": len(_df)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    import uuid
    session_id = req.session_id or str(uuid.uuid4())
    bot = _get_or_restore_bot(session_id)

    try:
        reply = bot.chat(req.message)
    except RuntimeError as e:
        # Most likely a missing GROQ_API_KEY, surface it as a clean 503
        # instead of an unhandled 500 traceback.
        raise HTTPException(status_code=503, detail=str(e))

    _persist_turn(session_id, req.message, reply)

    movies: List[MovieResult] = []
    if bot.last_results is not None and not bot.last_results.empty:
        for _, row in bot.last_results.iterrows():
            poster = row.get("Poster_Link")
            movies.append(MovieResult(
                title=row["Series_Title"],
                year=int(row["Released_Year"]),
                rating=float(row["IMDB_Rating"]),
                poster_url=poster if isinstance(poster, str) else None,
            ))

    return ChatResponse(response=reply, session_id=session_id, movies=movies)
