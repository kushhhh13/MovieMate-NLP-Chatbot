"""
Generation: this is the piece that was missing before. The old notebook's
generate_response() just formatted retrieved rows into an f-string. This
version sends the retrieved movies to an LLM (via LangChain's ChatGroq
wrapper) and asks it to write the actual reply. That's what makes this a
real retrieval-augmented generation pipeline instead of retrieval with a
templated printout.
"""

import os

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

_llm = None

SYSTEM_PROMPT = (
    "You are MovieMate, a friendly movie recommendation assistant. "
    "You are given a user's question and a list of movies retrieved from a "
    "database that match their query. Write a short, natural, conversational "
    "reply recommending these movies. Mention title, year, genre, and IMDb "
    "rating for each one. Only ever talk about the movies provided in the "
    "list, never invent or assume details about a movie that are not given "
    "to you. If the list says no movies were found, say so politely and "
    "suggest the user try different keywords."
)


def _get_llm():
    global _llm
    if _llm is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Export it as an environment variable "
                "before starting the app, e.g.: export GROQ_API_KEY=your_key_here"
            )
        _llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.4,
            max_tokens=400,
        )
    return _llm


def _format_context(results) -> str:
    if results.empty:
        return "No movies were found matching this query."

    lines = []
    for _, row in results.iterrows():
        lines.append(
            f"- {row['Series_Title']} ({row['Released_Year']}), "
            f"Genre: {row['Genre']}, Director: {row['Director']}, "
            f"IMDb Rating: {row['IMDB_Rating']}"
        )
    return "\n".join(lines)


def generate_response(query: str, results) -> str:
    context = _format_context(results)

    user_message = (
        f"User question: {query}\n\n"
        f"Retrieved movies:\n{context}\n\n"
        "Write the reply now."
    )

    llm = _get_llm()
    ai_message = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])
    return ai_message.content
