# 🎬 MovieMate — Conversational AI Movie Recommendation Chatbot

A conversational AI system that helps users discover movies through natural
language, built on retrieval-augmented generation (RAG): TF-IDF + FAISS for
retrieval, an LLM for generation, Django for persistent sessions and a
catalog admin, FastAPI serving it all, Docker to ship it.

---

## 📌 Project Overview

MovieMate lets users search for movies using natural language instead of
rigid filters. Instead of typing exact keywords, users can ask:

- *"Suggest thriller movies after 2000"*
- *"Best comedy movies from the 1990s"*
- *"Movies directed by Christopher Nolan"*
- *"Highly rated crime movies under 2 hours"*

---

## 📂 Dataset

**Source:** IMDb Top 1000 Movies Dataset
**Size:** 1000 movies, 16 features
**Key columns:** Title, Genre, Director, Cast, Rating, Runtime, Overview, Poster

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Pandas | Data cleaning and manipulation |
| Matplotlib / Seaborn | Exploratory data analysis (notebook) |
| Scikit-learn | TF-IDF vectorization |
| FAISS | Fast vector similarity search |
| LangChain (ChatGroq) + Groq (GPT-OSS 120B) | LLM-based response generation |
| FastAPI | Async API serving the chatbot |
| Django (ORM + admin) | Persistent chat sessions, movie catalog admin |
| Docker | Containerized deployment |
| Gradio | Local chat demo UI with poster thumbnails |
| Render | Live deployment (free tier) |

---

## 🧠 System Architecture

```
User Query
  ↓
Intent Parser (extracts year, genre, rating, runtime filters)
  ↓
TF-IDF Vectorizer (converts query to vector)
  ↓
FAISS Index Search (fast nearest neighbour retrieval)
  ↓
Post-retrieval Filtering (year, rating, runtime, genre)
  ↓
LLM Response Generation (LangChain + Groq, grounded in the retrieved movies)
  ↓
FastAPI /chat endpoint  →  session persisted via Django ORM (SQLite)
  ↓
Gradio demo UI (poster thumbnails)  or  any HTTP client
```

**Session persistence:** every turn is written to a `ChatSession`/
`ChatMessage` pair of Django models. If the FastAPI process restarts and a
client sends a `session_id` that's no longer in memory, the conversation is
looked up in the database and replayed instead of being lost.

**Django admin:** runs locally (`python manage.py runserver`) against the
same SQLite database, for browsing the movie catalog and chat history. It
is intentionally **not** deployed publicly, admin interfaces generally
shouldn't be internet-facing without real auth infrastructure in front of
them, so this is a deliberate scope decision, not a missing feature.

**Posters:** the dataset's `Poster_Link` column is carried through
retrieval and returned as structured data in the `/chat` response (and
rendered as thumbnails in the Gradio demo). The LLM is never asked to
reproduce poster URLs itself, they're attached to the reply afterward,
that avoids the model mangling or hallucinating image links.

---

## 📊 Key EDA Findings

- Ratings are **left skewed** — all movies are already elite (7.6–9.3)
- **Drama** is the most common genre, appearing in ~60% of movies
- Movies peak in the **2010s** — likely reflecting recency/internet bias
- **Alfred Hitchcock** has the most movies in the Top 1000
- **Weak correlation** (r=0.24) between runtime and rating
- **Moderate correlation** (r=0.50) between votes and rating

---

## 🚀 How to Run

### 1. Install dependencies

```bash
git clone https://github.com/kushsprite/MovieMate-NLP-Chatbot
cd MovieMate-NLP-Chatbot
pip install -r requirements-demo.txt   # includes gradio for the local demo
# or: pip install -r requirements.txt  # API-only, no gradio

export GROQ_API_KEY=your_key_here   # get one free at console.groq.com
```

### 2. Set up the database (Django)

```bash
python manage.py migrate
python manage.py createsuperuser     # for logging into /admin
python manage.py populate_movies     # loads the CSV into the Movie table
```

### 3a. Run the FastAPI service

```bash
uvicorn app.main:app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "suggest thriller movies after 2000"}'
```

### 3b. Run the Django admin (separate terminal, same database)

```bash
python manage.py runserver 8001
```

Visit `http://127.0.0.1:8001/admin`, log in with the superuser you created,
browse the Movie catalog and ChatSession/ChatMessage history.

### 3c. Run the Gradio demo (poster thumbnails)

```bash
python -m app.gradio_app
```

### 4. Docker

```bash
docker build -t moviemate .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here moviemate
```

The container runs migrations and populates the catalog automatically on
startup (see Dockerfile). Note: without a mounted persistent volume, the
SQLite file lives inside the container's writable layer, so it survives
an in-process restart but not a full container recreation, worth knowing
before deploying.

### 5. Deploy (Render, free tier)

1. Push this repo to GitHub (already done if you're reading this there)
2. Create a new Web Service on Render, connect the repo, choose **Docker**
   as the runtime
3. Add `GROQ_API_KEY` as an environment variable in the Render dashboard
4. Deploy. Render injects its own `PORT` env var, the Dockerfile's CMD
   already respects it (`${PORT:-8000}`)
5. Free tier note: the service spins down after inactivity and takes
   30-60 seconds to wake up on the next request

### Original notebook (Colab or local Jupyter)

1. Open `NLP_Project_MovieMate_Final.ipynb`
2. Upload `IMDB_Top_1000_Movies.csv` when prompted (Colab) or keep it in
   the same folder (local)
3. Run all cells, then use the Gradio interface at the bottom

Note: the notebook still contains the original template-based
`generate_response()`. The real LLM generation lives in `app/generation.py`
and is used by both the FastAPI service and `app/gradio_app.py`.

---

## 📁 Project Structure

```
MovieMate-NLP-Chatbot/
│
├── app/
│   ├── data_prep.py     # load and clean the CSV
│   ├── retrieval.py      # TF-IDF + FAISS retrieval
│   ├── intent.py           # natural language -> filter kwargs
│   ├── generation.py       # LLM-based response generation (LangChain + Groq)
│   ├── chatbot.py           # conversational flow, orchestrates the above
│   ├── main.py                # FastAPI app + Django-backed session persistence
│   └── gradio_app.py           # local demo UI with poster thumbnails
│
├── config/                # Django settings/urls/wsgi
├── movies/                 # Django app: Movie/ChatSession/ChatMessage models, admin
├── manage.py
│
├── README.md
├── NLP_Project_MovieMate_Final.ipynb   # original EDA + notebook demo
├── IMDB_Top_1000_Movies.csv
├── requirements.txt        # production deps (no gradio)
├── requirements-demo.txt   # adds gradio for the local demo
├── Dockerfile
├── .dockerignore
├── .gitignore
└── .env.example
```

---

## ⚠️ Limitations

- Dataset limited to Top 1000 IMDb movies — not a complete movie database
- Retrieval is TF-IDF based, it does not understand deep semantic meaning
  the way transformer embeddings would
- Recency bias in dataset — 2010s movies are overrepresented
- SQLite persistence survives process restarts but not container
  recreation without a mounted volume (see Docker section above)
- Django admin is local-only by design, not part of the public deployment
- IMDb voter base skews young and English speaking

---

## 🔮 Future Extensions

- Move from SQLite to a persistent hosted Postgres for true durability
  across redeploys
- Replace TF-IDF with sentence transformers for deeper semantic search
- Add user rating and personalisation features
- Add real authentication in front of the admin if it ever needs to be
  reachable outside a local machine

---

## 👤 Author

**Kushpreet Singh**
[GitHub](https://github.com/kushsprite) • [LinkedIn](https://linkedin.com/in/kushpreet-singh-)
