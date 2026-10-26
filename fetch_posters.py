
from pathlib import Path
import os
import time
import shutil

import pandas as pd
import requests
from dotenv import load_dotenv

# Project paths
ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "data" / "raw" / "tmdb_5000_movies.csv"
ENV_PATH = ROOT / ".env"
BACKUP_PATH = ROOT / "data" / "raw" / "tmdb_5000_movies_backup.csv"

# Load the token from .env
load_dotenv(ENV_PATH, override=True)
TOKEN = os.getenv("TMDB_ACCESS_TOKEN", "").strip()

if not TOKEN:
    raise SystemExit(
        "TMDB_ACCESS_TOKEN is missing. Check your .env file."
    )

if not CSV_PATH.exists():
    raise SystemExit(f"Movies CSV not found: {CSV_PATH}")

# Load the dataset
movies = pd.read_csv(CSV_PATH)

if "id" not in movies.columns:
    raise SystemExit("The movies CSV must contain an 'id' column.")

if "poster_path" not in movies.columns:
    movies["poster_path"] = ""

# Ensure poster paths are stored as text, not float64
movies["poster_path"] = (
    movies["poster_path"].astype("string").fillna("")
)

# Back up the original CSV once
if not BACKUP_PATH.exists():
    shutil.copy2(CSV_PATH, BACKUP_PATH)
    print("Original CSV backed up.")

# Save safely so progress is retained
def save_progress():
    temp_path = CSV_PATH.with_name("tmdb_5000_movies_temp.csv")
    movies.to_csv(temp_path, index=False)
    temp_path.replace(CSV_PATH)

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
})

total = len(movies)
updated = 0
missing = 0

print(f"Total movies: {total}")
print("Fetching poster paths...")

try:
    for position, (index, row) in enumerate(
        movies.iterrows(), start=1
    ):
        existing = str(movies.at[index, "poster_path"]).strip()

        # Do not fetch posters already available
        if existing and existing.lower() != "nan":
            continue

        movie_id = pd.to_numeric(row["id"], errors="coerce")

        if pd.isna(movie_id):
            missing += 1
            continue

        url = (
            f"https://api.themoviedb.org/3/movie/"
            f"{int(movie_id)}"
        )

        poster = ""
        success = False

        for attempt in range(5):
            try:
                response = session.get(url, timeout=20)
            except requests.RequestException as error:
                print(
                    f"Network issue for {row.get('title', movie_id)}: "
                    f"{error}"
                )
                time.sleep(2 * (attempt + 1))
                continue

            if response.status_code == 200:
                poster = response.json().get("poster_path") or ""
                success = True
                break

            if response.status_code == 401:
                save_progress()
                raise SystemExit(
                    "Authentication failed (401). "
                    "Check the token in .env."
                )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "5")
                try:
                    wait = max(1, int(retry_after))
                except ValueError:
                    wait = 5

                print(f"Rate limit reached. Waiting {wait} seconds...")
                time.sleep(wait)
                continue

            if response.status_code == 404:
                break

            if response.status_code >= 500:
                time.sleep(2 * (attempt + 1))
                continue

            print(
                f"Skipped {row.get('title', movie_id)}: "
                f"HTTP {response.status_code}"
            )
            break

        if success and poster:
            movies.at[index, "poster_path"] = poster
            updated += 1
        else:
            missing += 1

        # Save every 25 attempted rows
        if position % 25 == 0:
            save_progress()
            print(
                f"Checked {position}/{total} | "
                f"Added posters: {updated} | "
                f"Missing: {missing}"
            )

        # Avoid sending requests too quickly
        time.sleep(0.2)

finally:
    save_progress()
    session.close()

poster_count = (
    movies["poster_path"].fillna("").astype(str).str.strip().ne("").sum()
)

print("\nPoster fetching finished.")
print("Total movies:", total)
print("Movies with posters:", int(poster_count))
print("Movies without posters:", total - int(poster_count))
print("Updated CSV:", CSV_PATH)
