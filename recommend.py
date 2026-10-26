
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"

# Load the trained model files
movies = joblib.load(MODEL_DIR / "movies.pkl")
similarity = joblib.load(MODEL_DIR / "similarity.pkl")


def recommend_movies(movie_title, number_of_recommendations=5):
    # Find the movie by title (case-insensitive)
    matches = movies[
        movies["title"].fillna("").str.casefold()
        == movie_title.strip().casefold()
    ]

    if matches.empty:
        print(f"Movie '{movie_title}' was not found.")
        print("Please check the spelling or try another title.")
        return

    # Use the first matching movie
    movie_index = matches.index[0]

    # Get similarity scores and sort from highest to lowest
    scores = list(enumerate(similarity[movie_index]))
    scores = sorted(scores, key=lambda item: item[1], reverse=True)

    # Exclude the selected movie itself
    scores = [
        item for item in scores
        if item[0] != movie_index
    ]

    # Display recommendations
    print(f"\nMovies similar to: {movies.loc[movie_index, 'title']}")
    print("-" * 45)

    for rank, (index, score) in enumerate(
        scores[:number_of_recommendations], start=1
    ):
        print(
            f"{rank}. {movies.iloc[index]['title']} "
            f"(Similarity: {score:.3f})"
        )


if __name__ == "__main__":
    title = input("Enter a movie title (e.g., Avatar): ")
    recommend_movies(title)
