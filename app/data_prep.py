"""
Data loading and cleaning.

This is the same cleaning logic from the original notebook (Runtime, Released_Year,
Gross, Combined_Text), pulled into a reusable function instead of running top to
bottom in notebook cells.
"""

import pandas as pd


def load_and_clean_data(csv_path: str = "IMDB_Top_1000_Movies.csv") -> pd.DataFrame:
    dt = pd.read_csv(csv_path)
    dt_copy = dt.copy()

    # Runtime: "142 min" -> 142
    dt_copy["Runtime"] = dt_copy["Runtime"].str.replace(" min", "").astype(int)

    # Released_Year: one row has a non-numeric value (a stray "PG"), coerce to
    # NaN and drop it, same as the notebook.
    dt_copy["Released_Year"] = pd.to_numeric(dt_copy["Released_Year"], errors="coerce")
    dt_copy = dt_copy.dropna(subset=["Released_Year"])
    dt_copy["Released_Year"] = dt_copy["Released_Year"].astype(int)

    # Gross: strip symbols/commas, coerce to numeric (leaves NaN for the ~169
    # missing values, same as the notebook).
    dt_copy["Gross"] = pd.to_numeric(dt_copy["Gross"], errors="coerce")

    # Decade, used for "1990s"-style filters.
    dt_copy["Decade"] = (dt_copy["Released_Year"] // 10 * 10).astype(str) + "s"

    # Combined text field used for TF-IDF.
    dt_copy["Combined_Text"] = (
        dt_copy["Series_Title"] + " " +
        dt_copy["Genre"] + " " +
        dt_copy["Director"] + " " +
        dt_copy["Star1"] + " " +
        dt_copy["Star2"] + " " +
        dt_copy["Star3"] + " " +
        dt_copy["Star4"] + " " +
        dt_copy["Overview"]
    )

    return dt_copy.reset_index(drop=True)
