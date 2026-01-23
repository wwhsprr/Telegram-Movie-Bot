import asyncio
import logging
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from commands import (
    FILMS_COMMAND,
    FILM_CREATE_COMMAND,
    FILM_SEARCH_COMMAND,
    FILM_FILTER_COMMAND,
    FILM_DELETE_COMMAND,
    FILM_EDIT_COMMAND,
    BOT_COMMANDS,
    FILM_SEARCH_BY_ACTOR,
)


from data import edit_film, get_films, add_film, delete_film
from external import async_log_function_call
from functions import save_image
from keyboards import films_keyboard_markup, FilmCallback

from models import Film
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from aiogram.filters import Command


from config import BOT_TOKEN as TOKEN


class FilmForm(StatesGroup):

    name = State()
    description = State()
    year = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()


dp = Dispatcher()


@dp.message(Command("start"))
@async_log_function_call
async def start(message: Message) -> None:
    await message.answer("Привіт")


@dp.message(FILMS_COMMAND)
@async_log_function_call
async def films_list(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        "Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup,
    )


@dp.callback_query(FilmCallback.filter())
@async_log_function_call
async def callb_film(
    callback: CallbackQuery, callback_data: FilmCallback, state: FSMContext
) -> None:
    print(callback_data)
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    if callback_data.action == "info":
        text = (
            f"Фільм: {film.name}\n"
            f"Опис: {film.description}\n"
            f"Рейтинг: {film.rating}\n"
            f"Жанр: {film.genre}\n"
            f"Актори: {', '.join(film.actors)}\n"
        )

        await callback.message.answer_photo(
            caption=text,
            photo=FSInputFile(
                save_image(film.poster),
                filename=f"{film.name}_poster.{film.poster.split('.')[-1]}",
            ),
        )
    if callback_data.action == "edit":
        await state.set_state(MovieStates.edit_query)
        await get_edit_query(callback.message, state, film=film)
    if callback_data.action == "delete":
        await state.set_state(MovieStates.delete_query)
        await get_delete_query(callback.message, state, film=film)


@dp.message(FILM_CREATE_COMMAND)
@async_log_function_call
async def film_create(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmForm.name)
    await message.answer(
        "Введіть назву фільму.",
        reply_markup=None,
    )


@dp.message(FilmForm.name)
@async_log_function_call
async def film_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(
        "Введіть опис фільму.",
        reply_markup=None,
    )


@dp.message(FilmForm.description)
@async_log_function_call
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.year)
    await message.answer(
        "Введіть рік випуску фільму.",
        reply_markup=None,
    )


@dp.message(FilmForm.year)
@async_log_function_call
async def film_year(message: Message, state: FSMContext) -> None:
    try:
        year = int(message.text)
    except ValueError:
        await message.answer("Введіть коректний рік (число).")
        return

    await state.update_data(year=year)
    await state.set_state(FilmForm.rating)
    await message.answer(
        "Вкажіть рейтинг фільму від 0 до 10.",
        reply_markup=None,
    )


@dp.message(FilmForm.rating)
@async_log_function_call
async def film_rating(message: Message, state: FSMContext) -> None:
    try:
        float(message.text)
    except ValueError:
        await message.answer(
            "Введіть число",
            reply_markup=None,
        )
        return
    await state.update_data(rating=message.text)
    await state.set_state(FilmForm.genre)
    await message.answer(
        "Введіть жанр фільму.",
        reply_markup=None,
    )


@dp.message(FilmForm.genre)
@async_log_function_call
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.actors)
    await message.answer(
        text="Введіть акторів фільму через роздільник ', '\n"
        + html.bold("Обов'язкова кома та відступ після неї."),
        reply_markup=None,
    )


@dp.message(FilmForm.actors)
@async_log_function_call
async def film_actors(message: Message, state: FSMContext) -> None:
    await state.update_data(actors=[actor for actor in message.text.split(", ")])
    await state.set_state(FilmForm.poster)
    await message.answer(
        "Введіть посилання на постер фільму.",
        reply_markup=None,
    )


@dp.message(FilmForm.poster)
@async_log_function_call
async def film_poster(message: Message, state: FSMContext) -> None:
    data = await state.update_data(poster=message.text)
    film = Film(**data)
    add_film(film.model_dump())
    await state.clear()
    await message.answer(
        "Фільм збережено \n Натисніть /films для перегляду списку",
        reply_markup=None,
    )


class MovieStates(StatesGroup):

    search_query = State()
    search_actor_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()
    filter_genre = State()
    filter_year = State()
    filter_genre_year = State()


# Пошук фільму за назвою
@dp.message(FILM_SEARCH_COMMAND)
@async_log_function_call
async def search_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)


@dp.message(MovieStates.search_query)
@async_log_function_call
async def get_search_query(message: Message, state: FSMContext):
    query = message.text.lower()
    films = get_films()
    results = [film for film in films if query in film["name"].lower()]

    if results:
        for film in results:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")

    await state.clear()


# Фільтрація фільмів за жанром
@dp.message(FILM_FILTER_COMMAND)
@async_log_function_call
async def filter_movies(message: Message, state: FSMContext):
    await message.reply("Введіть жанр для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)


@dp.message(MovieStates.filter_criteria)
@async_log_function_call
async def get_filter_criteria(message: Message, state: FSMContext):
    films = get_films()
    criteria = message.text.lower()
    filtered = list(
        filter(lambda film: criteria in film["genre"].lower() == criteria, films)
    )

    if filtered:
        for film in filtered:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено за цими критеріями.")

    await state.clear()


# Видалення фільму за назвою
@dp.message(FILM_DELETE_COMMAND)
@async_log_function_call
async def delete_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)


@dp.message(MovieStates.delete_query)
@async_log_function_call
async def get_delete_query(message: Message, state: FSMContext, film=None):
    films = get_films()
    if not film:
        film_to_delete = message.text.lower()
    else:
        film_to_delete = film.name.lower()
    for film in films:
        if film_to_delete == film["name"].lower():
            delete_film(film)
            await message.reply(f"Фільм '{film['name']}' видалено.")
            await state.clear()
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()


# Редагування опису фільму за назвою
@dp.message(FILM_EDIT_COMMAND)
@async_log_function_call
async def edit_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)


@dp.message(MovieStates.edit_query)
@async_log_function_call
async def get_edit_query(message: Message, state: FSMContext, film=None):
    if not film:
        film_to_edit = message.text.lower()
    else:
        film_to_edit = film.name.lower()
    films = get_films()
    for film in films:
        if film_to_edit == film["name"].lower():
            await state.update_data(film=film)
            await message.reply("Введіть новий опис фільму:")
            await state.set_state(MovieStates.edit_description)
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()


@dp.message(MovieStates.edit_description)
@async_log_function_call
async def update_description(message: Message, state: FSMContext):
    data = await state.get_data()
    film = data["film"]
    film["description"] = message.text
    edit_film(film)
    await message.reply(f"Фільм '{film['name']}' оновлено.")
    await state.clear()


# Пошук фільмів за актором
@dp.message(FILM_SEARCH_BY_ACTOR)
@async_log_function_call
async def search_by_actor(message: Message, state: FSMContext):
    await message.reply("Введіть ім'я актора:")
    await state.set_state(MovieStates.search_actor_query)


@dp.message(MovieStates.search_actor_query)
@async_log_function_call
async def get_actor_search_query(message: Message, state: FSMContext):
    actor = message.text
    films = get_films(actor=actor)
    if films:
        for film in films:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")
    await state.clear()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="log.txt")
    asyncio.run(main())
