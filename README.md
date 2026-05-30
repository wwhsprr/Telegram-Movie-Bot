# Telegram Movie Bot 🎬

**Telegram Movie Bot** is a convenient tool for movie enthusiasts that helps organize your personal collection of watched movies and movies you plan to watch.

With this bot, you can create your own movie database by adding detailed information such as descriptions, posters, ratings, and cast members. Forget about keeping notes on your phone — now all your movies are available right in Telegram!

## 🚀 Features

The bot supports the following functionality:

* **View Movie List**: Display all saved movies with posters and detailed information.
* **Add Movies**: Save a movie title, description, release year, rating, genre, actors, and poster.
* **Search**:

  * By movie title.
  * By actor name.
* **Filter Movies**: Filter movies by genre.
* **Edit Movies**: Modify the description of an existing movie.
* **Delete Movies**: Remove movies from the database.

## 🛠 Technologies

* **Python 3.10+**
* **Aiogram 3.x** — for working with the Telegram API.
* **JSON** — for storing movie data.

## 📦 Installation and Setup

1. **Download the project or clone the repository:**

   ```bash
   git clone https://github.com/wwhsprr/Telegram-Movie-Bot.git
   cd telegram-movie-bot
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   For Windows:

   ```bash
   pip install aiogram aiofiles requests beautifulsoup4 pillow
   ```

4. **Configuration:**

   Open the `config.py` file and enter your bot token:

   ```python
   BOT_TOKEN = "YOUR_TOKEN"
   ```

5. **Run the bot:**

   ```bash
   python bot.py
   ```

## 🤖 Commands

| Command            | Description                 |
| ------------------ | --------------------------- |
| `/start`           | Start the bot               |
| `/films`           | Show all movies             |
| `/create_film`     | Add a new movie             |
| `/search_movie`    | Search for a movie by title |
| `/search_by_actor` | Search for a movie by actor |
| `/filter_movie`    | Filter movies by genre      |
| `/edit_movie`      | Edit a movie description    |
| `/delete_movie`    | Delete a movie              |

## 📂 Project Structure

* `bot.py` — main bot entry point.
* `handlers/` — (or corresponding modules) command handlers.
* `data.py` — data management (JSON).
* `films.json` — movie database.

---

Developed for personal use and learning purposes.
