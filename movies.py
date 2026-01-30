import random
import movie_storage_sql
from omdb_client import fetch_movie_from_omdb
import os

TEMPLATE_PATH = "index_template.html"
OUTPUT_PATH = "index.html"

def list_movies():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies in the database.")
        return

    print("\nMovies List:")
    for title, data in movies.items():
        rating = data.get("rating", "N/A")
        year = data.get("year", "N/A")
        print(f"- {title} | Rating: {rating} | Year: {year}")


def add_movie():
    title_input = input("Enter movie title: ").strip()
    if not title_input:
        print("No title entered.")
        return

    movies = movie_storage_sql.list_movies()
    if title_input in movies:
        print(f"Movie '{title_input}' already exists!")
        return

    try:
        movie_data = fetch_movie_from_omdb(title_input)
    except Exception as e:
        print(f"Error while contacting OMDb: {e}")
        return

    if movie_data is None:
        print(f"Movie '{title_input}' not found in OMDb.")
        return

    if movie_data["year"] is None or movie_data["rating"] is None:
        print("Could not retrieve valid year or rating from OMDb; movie not added.")
        return

    movie_storage_sql.add_movie(
        movie_data["title"],
        movie_data["year"],
        movie_data["rating"],
        movie_data["poster_url"],
    )
    print(f"Movie '{movie_data['title']}' added from OMDb.")

def delete_movie():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies to delete.")
        return

    name = input("Enter movie name to delete: ").strip()
    if name not in movies:
        print(f"Movie '{name}' was not found.")
        return

    movie_storage_sql.delete_movie(name)
    print(f"Movie '{name}' deleted.")


def update_movie():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies to update.")
        return

    name = input("Enter movie name to update: ").strip()
    if name not in movies:
        print(f"Movie '{name}' was not found.")
        return

    movie = movies[name]
    print(
        f"Current data: Title: {name}, "
        f"Rating: {movie.get('rating', 'N/A')}, "
        f"Year: {movie.get('year', 'N/A')}"
    )

    rating_input = input("Enter new rating (0-10, press Enter to keep current): ").strip()
    if not rating_input:
        print("No changes made.")
        return

    try:
        new_rating = float(rating_input)
        if not (0 <= new_rating <= 10):
            print("Invalid rating, keeping old rating.")
            return
    except ValueError:
        print("Invalid rating, keeping old rating.")
        return

    movie_storage_sql.update_movie(name, new_rating)
    print("Movie updated.")


def stats_movie():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies to calculate stats.")
        return

    ratings = [data["rating"] for data in movies.values() if "rating" in data]
    if not ratings:
        print("No ratings available to calculate stats.")
        return

    movie_count = len(ratings)
    avg_rating = sum(ratings) / movie_count

    sorted_ratings = sorted(ratings)
    if movie_count % 2 == 1:
        median_rating = sorted_ratings[movie_count // 2]
    else:
        mid1 = sorted_ratings[movie_count // 2 - 1]
        mid2 = sorted_ratings[movie_count // 2]
        median_rating = (mid1 + mid2) / 2

    max_rating = max(ratings)
    min_rating = min(ratings)

    best_movies = [title for title, data in movies.items() if data.get("rating") == max_rating]
    worst_movies = [title for title, data in movies.items() if data.get("rating") == min_rating]

    print("\nStats:")
    print(f"Movies count: {movie_count}")
    print(f"Average rating: {avg_rating:.2f}")
    print(f"Median rating: {median_rating:.2f}")
    print(f"Best movie(s): {', '.join(best_movies)} with rating {max_rating}")
    print(f"Worst movie(s): {', '.join(worst_movies)} with rating {min_rating}")


def random_movie():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies in the list.")
        return

    title = random.choice(list(movies.keys()))
    data = movies[title]
    print(
        f"Random movie: {title} | "
        f"Rating: {data.get('rating', 'N/A')} | "
        f"Year: {data.get('year', 'N/A')}"
    )


def search_movie():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies in the list.")
        return

    search = input("Enter movie name to search: ").strip().lower()
    found = False
    for title, data in movies.items():
        if search in title.lower():
            print(
                f"{title} | "
                f"Rating: {data.get('rating', 'N/A')} | "
                f"Year: {data.get('year', 'N/A')}"
            )
            found = True
    if not found:
        print(f"No movies found containing '{search}'.")


def sort_movies_by_rating():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies in the list.")
        return

    movies_with_rating = [
        (title, data) for title, data in movies.items() if "rating" in data
    ]
    if not movies_with_rating:
        print("No ratings available to sort.")
        return

    sorted_movies = sorted(
        movies_with_rating,
        key=lambda item: item[1]["rating"],
        reverse=True,
    )

    print("\nMovies Sorted By Rating:")
    for title, data in sorted_movies:
        print(f"{title}: {data['rating']}")


def sort_movies_by_year():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies in the list.")
        return

    movies_with_year = [
        (title, data) for title, data in movies.items() if "year" in data
    ]
    if not movies_with_year:
        print("No years available to sort.")
        return

    answer = input("Do you want the latest movies first? (Y/N): ").strip().lower()
    latest_first = answer.startswith("y")

    sorted_movies = sorted(
        movies_with_year,
        key=lambda item: item[1]["year"],
        reverse=latest_first,
    )

    print("\nMovies Sorted By Year:")
    for title, data in sorted_movies:
        print(f"{title} ({data['year']}) | Rating: {data.get('rating', 'N/A')}")


def filter_movies():
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies in the list.")
        return

    min_rating_input = input(
        "Enter minimum rating (leave blank for no minimum rating): "
    ).strip()
    start_year_input = input(
        "Enter start year (leave blank for no start year): "
    ).strip()
    end_year_input = input(
        "Enter end year (leave blank for no end year): "
    ).strip()

    min_rating = None
    if min_rating_input:
        try:
            min_rating = float(min_rating_input)
        except ValueError:
            print("Invalid minimum rating, ignoring rating filter.")
            min_rating = None

    start_year = None
    if start_year_input:
        try:
            start_year = int(start_year_input)
        except ValueError:
            print("Invalid start year, ignoring start year filter.")
            start_year = None

    end_year = None
    if end_year_input:
        try:
            end_year = int(end_year_input)
        except ValueError:
            print("Invalid end year, ignoring end year filter.")
            end_year = None

    filtered = []
    for title, data in movies.items():
        rating = data.get("rating")
        year = data.get("year")

        if min_rating is not None:
            if rating is None or rating < min_rating:
                continue

        if start_year is not None:
            if year is None or year < start_year:
                continue

        if end_year is not None:
            if year is None or year > end_year:
                continue

        filtered.append((title, data))

    if not filtered:
        print("No movies match the filter.")
        return

    print("\nFiltered movies:")
    for title, data in filtered:
        print(
            f"{title} | Rating: {data.get('rating', 'N/A')} | Year: {data.get('year', 'N/A')}"
        )

def generate_website():
    # 1. Load movies from DB
    movies = movie_storage_sql.list_movies()
    if not movies:
        print("No movies to include in the website.")
        return

    # 2. Read template file
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Template file '{TEMPLATE_PATH}' not found.")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_html = f.read()

    # 3. Build movie grid HTML
    movie_items = []
    for title, data in movies.items():
        year = data.get("year", "N/A")
        poster_url = data.get("poster_url") or ""

        item_html = f"""
        <li>
            <div class="movie">
                <img class="movie-poster" src="{poster_url}" alt="{title} poster">
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
            </div>
        </li>
        """.strip()
        movie_items.append(item_html)

    movie_grid_html = "\n".join(movie_items)

    # 4. Replace placeholders
    html_output = (
        template_html
        .replace("__TEMPLATE_TITLE__", "My Movie App")
        .replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)
    )

    # 5. Write index.html
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_output)

    print("Website was generated successfully.")

def main():
    while True:
        print("\nMenu")
        print("0. Exit")
        print("1. List movies")
        print("2. Add movie")
        print("3. Delete movie")
        print("4. Update movie")
        print("5. Stats")
        print("6. Random movie")
        print("7. Search movie")
        print("8. Movies sorted by rating")
        print("9. Movies sorted by year")
        print("10. Filter movies")
        print("11. Generate website")
        choice = input("Enter your choice (0-10): ").strip()

        if choice == "0":
            print("bye!")
            break
        elif choice == "1":
            list_movies()
        elif choice == "2":
            add_movie()
        elif choice == "3":
            delete_movie()
        elif choice == "4":
            update_movie()
        elif choice == "5":
            stats_movie()
        elif choice == "6":
            random_movie()
        elif choice == "7":
            search_movie()
        elif choice == "8":
            sort_movies_by_rating()
        elif choice == "9":
            sort_movies_by_year()
        elif choice == "10":
            filter_movies()
        elif choice == "11":
            generate_website()
        else:
            print("Invalid input, please enter a number between 0 and 10.")

        input("Press Enter to continue...")



if __name__ == "__main__":
    main()
