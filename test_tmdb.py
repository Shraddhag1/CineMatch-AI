
from pathlib import Path
import os
import requests
from dotenv import load_dotenv

# Load .env from the project folder
project_folder = Path(__file__).resolve().parent
load_dotenv(project_folder / ".env", override=True)

token = os.getenv("TMDB_ACCESS_TOKEN", "").strip()

print("Token loaded:", bool(token))
print(
    "Token format looks correct:",
    token.startswith("eyJ") and token.count(".") == 2
)

# Stop before making a request if the token is missing or malformed.
if not token or not (
    token.startswith("eyJ") and token.count(".") == 2
):
    raise SystemExit(
        "Check your .env file: use the long API Read Access Token."
    )

try:
    response = requests.get(
        "https://api.themoviedb.org/3/movie/19995",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        timeout=15
    )

    print("HTTP status:", response.status_code)

    if response.status_code == 200:
        movie = response.json()
        print("Authentication successful!")
        print("Movie:", movie.get("title"))
        print("Poster path:", movie.get("poster_path"))
    else:
        print("Error:", response.text[:500])

except requests.RequestException as error:
    print("Connection error:", error)
