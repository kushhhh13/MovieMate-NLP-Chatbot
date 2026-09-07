"""
Retrieval: TF-IDF + FAISS, exactly the same logic as the notebook's
search_movies() function, packaged as a class so the index is built once
at startup instead of once per notebook run.
"""

import faiss
from sklearn.feature_extraction.text import TfidfVectorizer


class MovieRetriever:
    def __init__(self, df):
        self.df = df
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            stop_words="english",
        )
        tfidf_matrix = self.vectorizer.fit_transform(df["Combined_Text"])
        tfidf_dense = tfidf_matrix.toarray().astype("float32")
        faiss.normalize_L2(tfidf_dense)

        dimension = tfidf_dense.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(tfidf_dense)

    def search(self, query, top_k=5, year_min=None, year_max=None,
               min_rating=None, max_runtime=None, genre_filter=None):
        query_vector = self.vectorizer.transform([query]).toarray().astype("float32")
        faiss.normalize_L2(query_vector)

        distances, indices = self.index.search(query_vector, k=50)
        distances = distances.flatten()
        indices = indices.flatten()

        results = self.df.iloc[indices].copy()
        results["Similarity_Score"] = distances.round(3)

        if year_min:
            results = results[results["Released_Year"] >= year_min]
        if year_max:
            results = results[results["Released_Year"] <= year_max]
        if min_rating:
            results = results[results["IMDB_Rating"] >= min_rating]
        if max_runtime:
            results = results[results["Runtime"] <= max_runtime]
        if genre_filter:
            results = results[results["Genre"].str.contains(genre_filter, case=False, na=False)]

        return results.head(top_k)[
            ["Series_Title", "Genre", "Director", "IMDB_Rating",
             "Released_Year", "Similarity_Score", "Poster_Link"]
        ]
