# 🎬 MovieMate — Conversational AI Movie Recommendation Chatbot

A conversational AI system that helps users discover movies through 
natural language interactions, built using NLP and Retrieval-Augmented 
Generation (RAG).

---

## 📌 Project Overview

MovieMate allows users to search for movies using natural language 
instead of rigid filters. Rather than typing exact keywords, users 
can ask questions like:

- *"Suggest thriller movies after 2000"*
- *"Best comedy movies from the 1990s"*
- *"Movies directed by Christopher Nolan"*
- *"Highly rated crime movies under 2 hours"*

---

## 📂 Dataset

**Source:** IMDb Top 1000 Movies Dataset  
**Size:** 1000 movies, 16 features  
**Key columns:** Title, Genre, Director, Cast, Rating, Runtime, Overview

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Pandas | Data cleaning and manipulation |
| Matplotlib / Seaborn | Exploratory data analysis |
| Scikit-learn | TF-IDF vectorization |
| FAISS | Fast vector similarity search |
| Gradio | Interactive chat interface |

---

## 🧠 System Architecture

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
Response Generator (formats conversational reply)
    ↓
Gradio Chat Interface


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

### Option 1 — Google Colab (Recommended)
1. Open `MovieMate_NLP_Project.ipynb` in Google Colab
2. Upload `IMDB_Top_1000_Movies.csv` when prompted
3. Run all cells
4. Click the Gradio public URL to open the chat interface

### Option 2 — Local
```bash
git clone https://github.com/kushhhh13/MovieMate-NLP-Chatbot
cd MovieMate-NLP-Chatbot
pip install -r requirements.txt
jupyter notebook MovieMate_NLP_Project.ipynb
```

---

## 📁 Project Structure

MovieMate-NLP-Chatbot/
│
├── README.md
├── MovieMate_NLP_Project.ipynb
├── IMDB_Top_1000_Movies.csv
└── requirements.txt


---

## ⚠️ Limitations

- Dataset limited to Top 1000 IMDb movies — not a complete movie database
- TF-IDF does not understand deep semantic meaning the way transformers do
- Recency bias in dataset — 2010s movies are overrepresented
- IMDb voter base skews young and English speaking

---

## 🔮 Future Extensions

- Replace TF-IDF with sentence transformers for deeper semantic search
- Integrate movie poster display in the chat interface
- Add user rating and personalisation features
- Deploy as a permanent web app using Hugging Face Spaces

---

## 👤 Author

**Kushpreet Singh**  
[GitHub](https://github.com/kushhhh13) • 
[LinkedIn](https://linkedin.com/in/kushpreet-singh-)
