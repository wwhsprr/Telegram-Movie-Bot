from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


class FilmCallback(CallbackData, prefix="films", sep=","):
    id: int
    name: str
    action: str


def films_keyboard_markup(
    films_list: list[dict], offset: int | None = None, skip: int | None = None
):
    builder = InlineKeyboardBuilder()

    for index, film_data in enumerate(films_list):
        info_cb = FilmCallback(id=index, action="info", **film_data)
        builder.row(
            InlineKeyboardButton(text=info_cb.name, callback_data=info_cb.pack())
        )

        edit_cb = FilmCallback(id=index, action="edit", **film_data)
        delete_cb = FilmCallback(id=index, action="delete", **film_data)

        builder.row(
            InlineKeyboardButton(text="edit", callback_data=edit_cb.pack()),
            InlineKeyboardButton(text="delete", callback_data=delete_cb.pack()),
            width=2,
        )

    return builder.as_markup()
