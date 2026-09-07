from django.contrib import admin

from .models import Movie, ChatSession, ChatMessage


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("series_title", "released_year", "genre", "imdb_rating", "runtime")
    list_filter = ("genre",)
    search_fields = ("series_title", "director", "overview")
    ordering = ("-imdb_rating",)


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "message", "created_at")
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "created_at", "updated_at", "message_count")
    readonly_fields = ("session_id", "created_at", "updated_at")
    inlines = [ChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"
