
from pathlib import Path

import joblib
from flask import Flask, render_template, request

app = Flask(__name__)

# Project paths
ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"

# Load trained model files
movies = joblib.load(MODEL_DIR / "movies.pkl")
similarity = joblib.load(MODEL_DIR / "similarity.pkl")


def recommend_movies(movie_title, limit=5):
    matches = movies[
        movies["title"].fillna("").str.casefold()
        == movie_title.strip().casefold()
    ]

    if matches.empty:
        return []

    movie_index = matches.index[0]
    scores = list(enumerate(similarity[movie_index]))
    scores.sort(key=lambda item: item[1], reverse=True)

    recommendations = []

    for index, score in scores:
        if index == movie_index:
            continue

        movie = movies.iloc[index]

        recommendations.append({
            "title": movie["title"],
            "overview": movie.get("overview", ""),
            "rating": movie.get("vote_average", 0),
            "poster_path": movie.get("poster_path", ""),
            "similarity": round(float(score), 3),
        })

        if len(recommendations) >= limit:
            break

    return recommendations


@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    search_title = ""
    error = ""

    if request.method == "POST":
        search_title = request.form.get("movie_title", "").strip()

        if not search_title:
            error = "Please enter a movie title."
        else:
            recommendations = recommend_movies(search_title)

            if not recommendations:
                error = (
                    f"No movie found for '{search_title}'. "
                    "Please check the title and try again."
                )

    return render_template(
        "index.html",
        recommendations=recommendations,
        search_title=search_title,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
