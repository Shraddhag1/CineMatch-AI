# 🎬 CineMatch AI — Movie Recommendation System

CineMatch AI is a content-based movie recommendation web app. Enter a movie title and the system recommends similar movies by comparing movie metadata such as overview, genres, keywords, cast, and other available text fields. The project uses Python, pandas, scikit-learn TF-IDF, cosine similarity, and Flask to serve recommendations through a web interface.

> **Project status:** The recommendation model has been trained on the TMDB 5000 Movies dataset. Poster images are optional and use poster paths from TMDB.

## Features

- **Content-based recommendations:** Suggests movies that are similar to a selected title.
- **TF-IDF text vectorization:** Converts the movie descriptions and metadata into numeric features.
- **Cosine similarity:** Compares movie feature vectors to rank similar titles.
- **Flask web interface:** Lets users search for a movie and browse recommendations.
- **Movie posters:** Displays poster images when a valid `poster_path` is available.
- **Reusable trained artifacts:** Saves the processed movie data, TF-IDF vectorizer, and similarity matrix for the app to use.

## Tech Stack

- **Language:** Python
- **Web framework:** Flask
- **Data handling:** pandas, NumPy
- **Machine learning:** scikit-learn (TF-IDF and cosine similarity)
- **Model/file utilities:** joblib / pickle
- **HTTP requests and configuration:** requests, python-dotenv
- **Frontend:** HTML, CSS, Jinja templates
- **Data source:** TMDB 5000 Movies and Credits dataset

## Project Structure

```text
CineMatch-AI/
├── app.py                         # Flask application
├── train_model.py                 # Builds and saves the recommendation model
├── recommend.py                   # Command-line movie recommendation script
├── fetch_posters.py               # Adds poster paths using the TMDB API
├── test_tmdb.py                   # Checks TMDB API authentication
├── requirements.txt               # Python dependencies
├── .env                           # Local secrets; do not commit this file
├── data/
│   ├── raw/
│   │   ├── tmdb_5000_movies.csv
│   │   └── tmdb_5000_credits.csv
│   └── processed/
│       └── movies_cleaned.csv
├── models/
│   ├── movies.pkl
│   ├── tfidf_vectorizer.pkl
│   └── similarity.pkl
├── src/
│   └── data_preprocessing.py      # Cleans and prepares movie data
├── notebooks/
│   └── exploratory_data_analysis.ipynb
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
└── templates/
    └── index.html                 # Main web page
```

*Some files or folders may be absent until you create them or run the relevant scripts.*

## Dataset

This project uses the TMDB 5000 Movies and Credits dataset. Place the two CSV files in `data/raw/`:

- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

Dataset source: [TMDB 5000 Movie Dataset on Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).

The raw movie CSV used during development did not initially include a `poster_path` column. The optional poster-fetching script adds this field by requesting movie details from TMDB using each movie's ID.

## Setup

### 1. Clone or open the project

Open the `CineMatch-AI` folder in VS Code, then open a terminal in the project root—the folder that contains `app.py` and `requirements.txt`.

### 2. Create and activate a virtual environment (recommended)

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If your virtual environment already exists (for example, `.venv-1`), activate that environment instead of creating another one.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

If installation reports that a pinned package version cannot be found, check the version in `requirements.txt` and use a version available for your Python version and platform.

### 4. Add the dataset

Make sure the two dataset CSV files are present in `data/raw/` before running preprocessing.

## Run the Project

Run commands from the main `CineMatch-AI` project folder, and run them in this order when preparing the project from scratch.

### 1. (Optional) Fetch movie poster paths

Poster fetching is optional. It requires a valid TMDB **API Read Access Token**. Create a `.env` file in the project root (at the same level as `app.py`) containing:

```text
TMDB_ACCESS_TOKEN=YOUR_TMDB_READ_ACCESS_TOKEN
```

Replace the placeholder locally with your own token. **Never publish your token, commit `.env`, or paste credentials into source code.** Add `.env` to `.gitignore`.

Install the HTTP and environment packages if they are not already installed:

```powershell
python -m pip install requests python-dotenv
```

Test authentication:

```powershell
python test_tmdb.py
```

A successful test prints HTTP status `200`, the movie title `Avatar`, and a poster path. Then fetch poster paths:

```powershell
python fetch_posters.py
```

This script makes requests for movies that do not already have a poster path, saves progress periodically, and backs up the original movie CSV. It may take time and some movies may not have a poster available. If you do not want to use the TMDB API, skip this step; recommendations can still work without posters.

### 2. Preprocess the data

```powershell
python src/data_preprocessing.py
```

This should create or update `data/processed/movies_cleaned.csv`.

### 3. Train the recommendation model

```powershell
python train_model.py
```

The model-training script should save the processed movie data, TF-IDF vectorizer, and similarity matrix in the `models/` folder. In development, the TF-IDF matrix was reported as `(4803, 10000)` and the similarity matrix as `(4803, 4803)`.

### 4. Start the Flask app

```powershell
python app.py
```

Open the local address printed by Flask in your browser (commonly `http://127.0.0.1:5000/`). Enter a movie title and view the recommended movies.

### Optional: Run recommendations in the terminal

```powershell
python recommend.py
```

Follow the prompt to enter a movie title, such as `Avatar`.

## How It Works

1. **Preprocessing:** Movie and credits data are combined and cleaned. Relevant text fields are prepared for recommendation.
2. **Feature creation:** TF-IDF converts the combined text into a sparse numerical feature matrix.
3. **Similarity calculation:** Cosine similarity compares the movie vectors and ranks similar movies.
4. **Recommendation:** The system looks up a selected movie and returns titles with the highest similarity scores, excluding the selected movie itself.
5. **Web display:** Flask passes the recommendations to the HTML template. If `poster_path` is available, the template can load a TMDB image using the image URL format below.

```text
https://image.tmdb.org/t/p/w500/POSTER_PATH
```

For example, a poster path such as `/example.jpg` is appended to the base URL. Poster availability depends on TMDB data and image access.

## Example

During development, searching for `Avatar` in the command-line recommender returned titles such as `Aliens`, `Alien³`, `Moonraker`, `Alien`, and `Silent Running`, each with a similarity score. Recommendations can change if the dataset, preprocessing, or model settings change.

## Troubleshooting

- **`FileNotFoundError` for a CSV:** Check that both raw dataset CSVs are inside `data/raw/` and that you run commands from the project root.
- **`poster_path` is missing:** Run `fetch_posters.py` after configuring a valid token, or allow preprocessing to set missing poster paths to an empty string.
- **TMDB returns HTTP 401:** Confirm that `.env` contains a valid API Read Access Token (not the shorter v3 API key), that the variable is named `TMDB_ACCESS_TOKEN`, and that `test_tmdb.py` loads `.env` from the project root. Do not share the token.
- **Posters do not appear:** Inspect a few values in `data/raw/tmdb_5000_movies.csv` and `data/processed/movies_cleaned.csv`. Non-empty poster paths should look like `/some_file.jpg`. Verify the HTML template uses the `poster_path` value and that the browser can reach TMDB's image host.
- **A package install fails:** Confirm that the correct virtual environment is active and that the package versions in `requirements.txt` are available for your Python version.
- **The app cannot find model files:** Run preprocessing and `train_model.py` before starting `app.py`.

## Security

Recommended `.gitignore` entries:

```gitignore
.env
.venv/
.venv-1/
__pycache__/
*.py[cod]
```

Never commit API tokens, private credentials, or other secrets to GitHub. If a token has been exposed, revoke or regenerate it in your TMDB account settings.

## Limitations

- Recommendations are based on metadata text similarity, not personal preferences or collaborative user behavior.
- Similarity does not guarantee that two movies will appeal to the same viewer.
- Poster paths may be absent for some movies, and fetching them requires a valid TMDB API token and network access.

## Possible Future Improvements

- Add genre, release year, and rating filters.
- Add fuzzy title matching and a clearer message when a title is not found.
- Add pagination and a larger number of recommendations.
- Improve the UI with loading states and fallback images for unavailable posters.
- Add automated tests for preprocessing, recommendations, and Flask routes.

## Acknowledgements

- [TMDB](https://www.themoviedb.org/) for movie metadata and poster images.
- [The Movie Database dataset on Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) for the movie and credits CSV files.

This project is intended for learning and demonstration. Review the dataset's terms and TMDB's attribution and API/image-use requirements before publishing or deploying it.
