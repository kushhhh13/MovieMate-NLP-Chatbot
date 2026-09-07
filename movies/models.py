from django.db import models


class Movie(models.Model):
    """
    The canonical movie catalog, browsable and editable through the admin.
    This is separate from the pandas DataFrame the FastAPI service loads
    into memory for fast TF-IDF/FAISS retrieval, that separation is
    intentional: the admin manages the catalog, the API optimizes for
    read speed. They're kept in sync via the populate_movies command.
    """
    series_title = models.CharField(max_length=255)
    released_year = models.IntegerField()
    genre = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    imdb_rating = models.FloatField()
    runtime = models.IntegerField(help_text="Minutes")
    overview = models.TextField(blank=True)
    poster_url = models.URLField(blank=True, max_length=500)

    class Meta:
        ordering = ["-imdb_rating"]

    def __str__(self):
        return f"{self.series_title} ({self.released_year})"


class ChatSession(models.Model):
    """One row per conversation. session_id matches the id FastAPI hands
    back to the client, so a restarted FastAPI process can look up and
    resume a conversation instead of losing it."""
    session_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.session_id


class ChatMessage(models.Model):
    ROLE_CHOICES = [("user", "User"), ("bot", "Bot")]

    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        preview = self.message[:50]
        return f"[{self.role}] {preview}"
