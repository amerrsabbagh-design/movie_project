import os
import requests

OMDB_API_KEY = "1d7cd6cf"
BASE_URL = "http://www.omdbapi.com/"

class OmdbError(Exception):
    pass

def fetch_movie_from_omdb(title: str) -> dict | None:
    if not OMDB_API_KEY:
        raise OmdbError("OMDb API key is missing.")

    params = {"apikey": OMDB_API_KEY, "t": title}

    try:
        resp = requests.get(BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Covers no internet, DNS issues, timeout, 5xx, etc.
        raise OmdbError(f"Could not reach OMDb API: {e}")

    data = resp.json()

    # Movie not found in OMDb
    if data.get("Response") == "False":
        return None

    year_raw = data.get("Year")
    imdb_raw = data.get("imdbRating")

    year = int(year_raw) if year_raw and year_raw.isdigit() else None
    rating = float(imdb_raw) if imdb_raw not in (None, "N/A") else None

    return {
        "title": data.get("Title"),
        "year": year,
        "rating": rating,
        "poster_url": data.get("Poster"),
    }
