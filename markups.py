from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard():
    button_list = [
        [KeyboardButton("🎿 Оформить заказ"),
         KeyboardButton("📕 Правила хранения")],
        [KeyboardButton("📦 Мои заказы")]
    ]
    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
    return reply_markup


""" Раздел Мои заказы """


def take_items_choice_keyboard():
    button_list = [
        [InlineKeyboardButton("Забрать все вещи", callback_data='take_items_all'),
         InlineKeyboardButton("Забрать часть вещей", callback_data='take_items_partial')]
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    return reply_markup


def take_items_back_delivery_keyboard():
    button_list = [
        [InlineKeyboardButton("Доставка (платная)", callback_data='take_items_back_delivery'),
         InlineKeyboardButton("Самовывоз", callback_data='take_items_back_myself')]
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    return reply_markup


""" Раздел Оформить Заказ"""


def box_size_keyboard():
    button_list = [
        [InlineKeyboardButton("📦 S-Size", callback_data='S-size'),
         InlineKeyboardButton("📦 M-Size", callback_data='M-size')],
        [InlineKeyboardButton("📦 L-Size", callback_data='L-size'),
         InlineKeyboardButton("📦 >L-Size", callback_data='>L-size')],
        [InlineKeyboardButton("❌ Я не хочу замерять сам", callback_data='dont_want_measure')]
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    return reply_markup


def storage(addresses):
    num_addresses = len(addresses)
    num_rows = (num_addresses // 2) + (num_addresses % 2)

    button_list = []
    for row in range(num_rows):
        if row == num_rows - 1 and num_addresses % 2 != 0:
            button_list.append([KeyboardButton(f"🏪 {addresses[-1]}")])
        else:
            button_list.append([
                KeyboardButton(f"🏪 {addresses[row * 2]}"),
                KeyboardButton(f"🏪 {addresses[row * 2 + 1]}")
            ])
    button_list.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
    return reply_markup
