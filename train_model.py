
from pathlib import Path

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Project paths
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "processed" / "movies_cleaned.csv"
MODEL_DIR = ROOT / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Load cleaned movie data
movies = pd.read_csv(DATA_FILE)

# Handle missing text
movies["combined_features"] = (
    movies["combined_features"].fillna("").astype(str)
)

print("Movies loaded:", movies.shape)

# Convert movie descriptions into numerical features
tfidf = TfidfVectorizer(
    stop_words="english",
    max_features=10000
)

tfidf_matrix = tfidf.fit_transform(movies["combined_features"])

# Calculate similarity between movies
similarity_matrix = cosine_similarity(tfidf_matrix)

# Save trained components
joblib.dump(movies, MODEL_DIR / "movies.pkl")
joblib.dump(tfidf, MODEL_DIR / "tfidf_vectorizer.pkl")
joblib.dump(similarity_matrix, MODEL_DIR / "similarity.pkl")

print("\nModel training completed successfully!")
print("TF-IDF matrix shape:", tfidf_matrix.shape)
print("Similarity matrix shape:", similarity_matrix.shape)
print("Saved model files to:", MODEL_DIR)
