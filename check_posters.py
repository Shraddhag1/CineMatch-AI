
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent

movies_path = root / "data" / "raw" / "tmdb_5000_movies.csv"
credits_path = root / "data" / "raw" / "tmdb_5000_credits.csv"

movies = pd.read_csv(movies_path)
credits = pd.read_csv(credits_path)

print("Movies columns:")
print(movies.columns.tolist())

print("\nCredits columns:")
print(credits.columns.tolist())

print("\nFirst 5 credits rows:")
print(credits[["movie_id", "title"]].head().to_string(index=False))
