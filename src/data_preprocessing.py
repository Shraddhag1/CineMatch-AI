
from pathlib import Path
import json
import ast
import pandas as pd


# --------------------------------------------------
# 1. Set up file paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MOVIES_FILE = RAW_DIR / "tmdb_5000_movies.csv"
CREDITS_FILE = RAW_DIR / "tmdb_5000_credits.csv"
OUTPUT_FILE = PROCESSED_DIR / "movies_cleaned.csv"


# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

movies = pd.read_csv(MOVIES_FILE)
credits = pd.read_csv(CREDITS_FILE)

print("Movies loaded:", movies.shape)
print("Credits loaded:", credits.shape)


# --------------------------------------------------
# 3. Parse JSON-like columns safely
# --------------------------------------------------

def parse_json_column(value):
    if pd.isna(value) or value == "":
        return []

    try:
        result = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        try:
            result = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []

    return result if isinstance(result, list) else []


def extract_names(value):
    items = parse_json_column(value)

    return [
        item["name"]
        for item in items
        if isinstance(item, dict) and item.get("name")
    ]


def extract_director(value):
    items = parse_json_column(value)

    for item in items:
        if (
            isinstance(item, dict)
            and item.get("job") == "Director"
        ):
            return item.get("name", "")

    return ""


def clean_text(value):
    if pd.isna(value):
        return ""

    return " ".join(str(value).strip().split())


# --------------------------------------------------
# 4. Clean movie records
# --------------------------------------------------

movies = movies.dropna(subset=["id", "title"]).copy()

movies["id"] = pd.to_numeric(
    movies["id"], errors="coerce"
)

movies = movies.dropna(subset=["id"]).copy()
movies["id"] = movies["id"].astype("int64")

movies = movies.drop_duplicates(subset=["id"])
credits["movie_id"] = pd.to_numeric(
    credits["movie_id"], errors="coerce"
)

credits = credits.dropna(subset=["movie_id"]).copy()
credits["movie_id"] = credits["movie_id"].astype("int64")
credits = credits.drop_duplicates(subset=["movie_id"])


# --------------------------------------------------
# 5. Extract genres and keywords
# --------------------------------------------------

movies["genres_list"] = movies["genres"].apply(extract_names)
movies["keywords_list"] = movies["keywords"].apply(extract_names)

movies["genres_text"] = movies["genres_list"].apply(
    lambda items: " ".join(items)
)

movies["keywords_text"] = movies["keywords_list"].apply(
    lambda items: " ".join(items)
)


# --------------------------------------------------
# 6. Extract cast and director from credits
# --------------------------------------------------

credits["cast_list"] = credits["cast"].apply(extract_names)
credits["director"] = credits["crew"].apply(extract_director)

# Keep the first five listed cast members
credits["cast_text"] = credits["cast_list"].apply(
    lambda items: " ".join(items[:5])
)


# --------------------------------------------------
# 7. Merge movies and credits
# --------------------------------------------------

data = movies.merge(
    credits[["movie_id", "cast_text", "director"]],
    left_on="id",
    right_on="movie_id",
    how="left",
    validate="one_to_one"
)


# --------------------------------------------------
# 8. Handle missing values
# --------------------------------------------------

text_columns = [
    "title",
    "overview",
    "genres_text",
    "keywords_text",
    "cast_text",
    "director",
]

for column in text_columns:
    data[column] = data[column].apply(clean_text)

for column in ["vote_average", "vote_count", "popularity"]:
    data[column] = pd.to_numeric(
        data[column], errors="coerce"
    ).fillna(0)


# --------------------------------------------------
# 9. Create combined text for machine learning
# --------------------------------------------------

data["combined_features"] = (
    data["genres_text"] + " "
    + data["keywords_text"] + " "
    + data["overview"] + " "
    + data["cast_text"] + " "
    + data["director"]
).str.lower().str.strip()

# Remove records with no useful recommendation text
data = data[
    data["combined_features"].str.len() > 0
].copy()


# --------------------------------------------------
# 10. Select useful columns and save
# --------------------------------------------------

columns_to_keep = [
    "id",
    "title",
    "overview",
    "genres_text",
    "keywords_text",
    "cast_text",
    "director",
    "release_date",
    "vote_average",
    "vote_count",
    "popularity",
    "poster_path",
    "combined_features",
]
if "poster_path" not in data.columns:
    data["poster_path"] = ""
data = data[columns_to_keep]

data.to_csv(OUTPUT_FILE, index=False)

print("\nPreprocessing completed!")
print("Cleaned dataset shape:", data.shape)
print("Saved to:", OUTPUT_FILE)
print("\nFirst five cleaned movies:")
print(data[["title", "genres_text", "director"]].head())

print("\nRemaining missing values:")
print(data.isnull().sum())
