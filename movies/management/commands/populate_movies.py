from django.core.management.base import BaseCommand

from app.data_prep import load_and_clean_data
from movies.models import Movie


class Command(BaseCommand):
    help = "Load IMDB_Top_1000_Movies.csv into the Movie table (clears existing rows first)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-path",
            default="IMDB_Top_1000_Movies.csv",
            help="Path to the CSV file (default: IMDB_Top_1000_Movies.csv in the repo root)",
        )

    def handle(self, *args, **options):
        df = load_and_clean_data(options["csv_path"])

        Movie.objects.all().delete()

        movies = [
            Movie(
                series_title=row["Series_Title"],
                released_year=int(row["Released_Year"]),
                genre=row["Genre"],
                director=row["Director"],
                imdb_rating=float(row["IMDB_Rating"]),
                runtime=int(row["Runtime"]),
                overview=row["Overview"],
                poster_url=row["Poster_Link"] if isinstance(row["Poster_Link"], str) else "",
            )
            for _, row in df.iterrows()
        ]
        Movie.objects.bulk_create(movies)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(movies)} movies into the database."))
