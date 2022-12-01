from telebot import types

def make_kb(buttons: dict, row_width=3):
    # [(text, callback_data), ...]
    keyboard = types.InlineKeyboardMarkup(row_width=row_width)

    for data, text in buttons.items():
        keyboard.add(
                types.InlineKeyboardButton(
                    text=text,
                    callback_data=data
                )
        )

    return keyboard

