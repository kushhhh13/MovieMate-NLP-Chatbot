"""
Intent parsing: turns a natural-language query into search_movies() filter
kwargs. Unchanged from the notebook, this logic was already solid.
"""

import re


def parse_intent(text: str) -> dict:
    text_lower = text.lower()
    filters = {}

    # Year filters: "after 2000", "before 1990", "in 1994"
    after_match = re.search(r'after\s+(\d{4})', text_lower)
    before_match = re.search(r'before\s+(\d{4})', text_lower)
    in_match = re.search(r'in\s+(\d{4})', text_lower)

    if after_match:
        filters['year_min'] = int(after_match.group(1))
    if before_match:
        filters['year_max'] = int(before_match.group(1))
    if in_match:
        filters['year_min'] = int(in_match.group(1))
        filters['year_max'] = int(in_match.group(1))

    # Decade filter: "1990s", "2000s"
    decade_match = re.search(r'(\d{4})s', text_lower)
    if decade_match:
        decade = int(decade_match.group(1))
        filters['year_min'] = decade
        filters['year_max'] = decade + 9

    # Rating filters
    if any(word in text_lower for word in ['highly rated', 'top rated', 'best']):
        filters['min_rating'] = 8.5
    elif 'good' in text_lower:
        filters['min_rating'] = 7.5

    rating_match = re.search(r'rating\s*(above|over|greater than)\s*(\d+\.?\d*)', text_lower)
    if rating_match:
        filters['min_rating'] = float(rating_match.group(2))

    # Runtime filter: "under 2 hours", "less than 120 minutes"
    hours_match = re.search(r'under\s+(\d+)\s+hour', text_lower)
    mins_match = re.search(r'less than\s+(\d+)\s+min', text_lower)

    if hours_match:
        filters['max_runtime'] = int(hours_match.group(1)) * 60
    if mins_match:
        filters['max_runtime'] = int(mins_match.group(1))

    # Genre filter
    genres = ['action', 'comedy', 'drama', 'crime', 'thriller',
              'romance', 'horror', 'adventure', 'animation',
              'sci-fi', 'fantasy', 'mystery', 'biography', 'history']
    for genre in genres:
        if genre in text_lower:
            filters['genre_filter'] = genre.title()
            break

    return filters
