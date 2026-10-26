
from pathlib import Path
import pandas as pd

data_folder = Path("data/raw")

movies_file = data_folder / "tmdb_5000_movies.csv"
credits_file = data_folder / "tmdb_5000_credits.csv"

# Check whether the files exist
for file in [movies_file, credits_file]:
    if not file.exists():
        raise FileNotFoundError(
            f"Missing file: {file.resolve()}"
        )

# Load the datasets
movies = pd.read_csv(movies_file)
credits = pd.read_csv(credits_file)

print("Dataset loaded successfully!")
print("\nMovies dataset shape:", movies.shape)
print("Credits dataset shape:", credits.shape)

print("\nMovies columns:")
print(movies.columns.tolist())

print("\nCredits columns:")
print(credits.columns.tolist())

print("\nFirst 5 movies:")
print(movies[["id", "title", "genres"]].head())

print("\nMissing values in movies:")
print(movies.isnull().sum().sort_values(ascending=False).head(10))
