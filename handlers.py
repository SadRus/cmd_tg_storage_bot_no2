import db_handler
import markups as m
import sqlalchemy
import re

from telegram import ReplyKeyboardRemove
from db import Base, Customer, Orders, Storage, Box


def start(update, context):
    hello_message_to_new_user = (
        "Вас приветствует *Garbage Collector* — Склад индивидуального хранения!\n"
        "Вас интересует аренда бокса? С радостью проконсультируем по нашим услугам.\n"
        "А пока посмотрите примеры и тд...,\n"
    )
    first_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    try:
        db_handler.add_customer(first_name, user_id)
    except sqlalchemy.exc.IntegrityError:
        print('Пользователь уже зарегистрирован')
    photo_path = 'media/storage.jpg'
    with open(photo_path, 'rb') as file:
        update.message.reply_photo(
            photo=file,
            caption=f"Приветствуем Вас *{first_name}*, {hello_message_to_new_user}\n"
                    f"[*ОСТОРОЖНО РЕКЛАМА*](bit.ly/41Mqpoj)",
            reply_markup=m.start_keyboard(),
            parse_mode='markdown'
        )
    return 0


def user_input(update, context):
    text = update.message.text
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if text == "🎿 Оформить заказ":
        storage_address = db_handler.get_storage_address()
        # INLINE MENU
        update.message.reply_text(
            'Мы предоставляем стандартные размеры коробок для хранения. Если вы знаете точный размер, выберите '
            'подходящий для вас вариант. \nЕсли же вы не уверены в нужном размере, наши консультанты помогут вам '
            'выбрать подходящую коробку при вашем визите на склад.\nТакже наш курьер может замерить необходимые '
            'параметры, чтобы помочь вам определиться с выбором.\n'
            f'Наш склад находиться по адресу: *{storage_address}*',
            parse_mode='Markdown',
            reply_markup=m.box_size_keyboard()
        )
        return 0  # ORDERS

    elif text == "📕 Правила хранения":
        storage_rules = 'Спасибо, что выбрали наш сервис сезонного хранения вещей *Garbage Collector*. Наше хранилище ' \
                        'не принимает в хранение *жидкости, наркотики, биткоины, оружие и другие неприемлемые вещи*. ' \
                        'У нас есть ограничение на количество хранимых вещей. Хранение происходит на свой страх и ' \
                        'риск. *Пожалуйста, забирайте свои вещи вовремя*, чтобы избежать огромных финансовых потерь. '
        update.message.reply_text(storage_rules, parse_mode='Markdown')

    elif text == "📦 Мои заказы":
        orders = db_handler.get_customer_orders(user_id)
        if orders:
            update.message.reply_text(
                'Выберите номер заказа:',
                parse_mode='Markdown',
                reply_markup=m.customer_orders_keyboard(orders)
            )
            return 5  # MY_ORDERS
        else:
            update.message.reply_text(
                text=(
                    'Простите, но кажется у вас еще нет барахла на хранении 😞\n'
                    'Пожалуйста оформите заказ.'
                ),
                parse_mode='Markdown',
                # кнопки назад?
            )


# Ветка Оформить заказ


def box_size_inline_menu(update, context):
    query = update.callback_query
    query.answer()
    if query.data in ['S', 'M', 'L', 'XL']:
        context.user_data['box_size'] = query.data
        text = f'Вы выбрали бокс *{context.user_data["box_size"]}-размера*\n' \
               'Пожалуйста выберите срок хранения.\n' \
               'Мы рады предложить Вам следующие варианты:'
        query.edit_message_text(
            text=text,
            reply_markup=m.storage_periods_keyboard(),
            parse_mode='markdown'
        )
    elif query.data == 'dont_want_measure':
        context.user_data['box_size'] = 'Будет уточнен'
        text = 'Хорошо, мы замерим сами когда вы приедете на склад или замерит наш курьер'
        query.edit_message_text(
            text=text,
            reply_markup=m.storage_periods_keyboard()
        )
        context.user_data['box_size'] = 'Unknown'
    return 0  # ORDERS


def month_spelling(num_month):
    if num_month == 1:
        return 'месяц'
    elif num_month in [2, 3, 4]:
        return 'месяца'
    else:
        return 'месяцев'


def storage_period_inline_menu(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['period'] = int(query.data.split('_')[0])
    if query.data in ['1_month', '3_month', '6_month', '12_month']:
        # Orders.period = int(query.data.split('_')[0])
        text = f'Отлично, вы хотите поместить коробку размером' \
               f'\n*{context.user_data["box_size"]}* на срок' \
               f' *{context.user_data["period"]} {month_spelling(context.user_data["period"])}*.\n' \
               f'Пожалуйста выберите способ доставки:\n' \
               f'Курьерская служба *(абсолютно бесплатно)*\n' \
               f'Привезете сами на наш склад по адресу: {db_handler.get_storage_address()}'
        query.edit_message_text(
            text=text,
            reply_markup=m.is_delivery_keyboard(),
            parse_mode='markdown'
        )
    return 1  # DELIVERY


def is_delivery_inline_menu(update, context):
    query = update.callback_query
    query.answer()
    is_delivery = {
        'delivery': 1,
        'self_delivery': 0
    }
    if query.data == 'delivery':
        # Orders.is_delivery = is_delivery_value[query.data]
        text = 'Прекрасно, вы выбрали доставку курьерской службой:\n' \
               'Нам потребуются ваши контактные данные.\n' \
               'Но прежде чем продолжить, пожалуйста примите\n' \
               '*Согласие на обработку персональных данных*'
        query.edit_message_text(
            text=text,
            reply_markup=m.personal_data_agreement_keyboard(),
            parse_mode='markdown'
        )
    if query.data == 'self_delivery':
        # Orders.is_delivery = is_delivery_value[query.data]
        text = f'Прекрасно, вы привезете вещи сами по адресу:\n*{db_handler.get_storage_address()}*\n' \
               'Нам потребуются ваши контактные данные.\n' \
               'Но прежде чем продолжить, пожалуйста примите\n' \
               '*Согласие на обработку персональных данных*'
        query.edit_message_text(
            text=text,
            reply_markup=m.personal_data_agreement_keyboard(),
            parse_mode='markdown'
        )
    context.user_data['is_delivery'] = is_delivery[query.data]
    return 2  # PERSONAL_DATA


def personal_data_menu(update, context):
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    print(user_data)
    if query.data == 'accept':
        db_handler.create_order(
            customer_id=user_data['user_id'],
            box_size=user_data['box_size'],
            period=user_data['period'],
            is_delivery=user_data['is_delivery'],
        )
        query.edit_message_text(
            text=(
                'Отлично, ваш заказ почти сформирован.\n'
                'Напишите номер телефона для связи в формате\n*+7-XXX-XXX-XX-XX*\n'
                '\nЕсли вы не увидели сообщение о вводе электронной почты, значит формат телефона неверный'
                'поробуйте еще раз'
            ),
            parse_mode='markdown',
        )
        return 3  # CUSTOMER_PHONE
    if query.data == 'not_accept':
        query.edit_message_text(
            text='Нам очень жаль, но для оформления заказа необходимо принять соглашение'
        )


def write_customer_phone(update, context):
    text = update.message.text
    db_handler.add_phone_to_customer(context.user_data['user_id'], phone=text)
    update.message.reply_text(
        'Отлично! Теперь введите email для отправки уведомлений.'
        'Если вы не увидели сообщение об успешном оформлении заказа, '
        'скорее всего вы ввели некоректный адрес электронной почты.'
        '\nПример адреса: *example@mail.ru*',
        parse_mode='markdown'
    )
    return 4  # CUSTOMER EMAIL


def write_customer_email(update, context):
    text = update.message.text
    db_handler.add_email_to_customer(context.user_data['user_id'], email=text)
    update.message.reply_text('Супер! Заказ оформлен.')


# Ветка Мои заказы


def take_item_back_inline_menu(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'take_items_all':
        text = 'Вы собираетесь забрать все вещи:\nПожалуйста выберите способ доставки'
        query.edit_message_text(
            text=text,
            reply_markup=m.take_items_back_delivery_keyboard()
        )
    elif query.data == 'take_items_partial':
        text = 'Вы собираетесь забрать лишь часть вещей:\nПожалуйста выберите способ доставки'
        query.edit_message_text(
            text=text,
            reply_markup=m.take_items_back_delivery_keyboard()
        )
    elif query.data == 'take_items_back_delivery':
        user_id = context.user_data['user_id']
        customer_phone = db_handler.get_customer_phone(user_id)
        text = 'Отлично с вами свяжется наш специалист и уточнит информацию по доставке' \
               f'\nПожалуйта проверьте ваш номер телефона: *{customer_phone}*' \
               f'\nЕсли ваш номер телефона изменился, пожалуйста введите новый.' \
               f'\nЕсли телефон верный, ожидайте звонка. Спасибо'
        query.edit_message_text(
            text=text,
            parse_mode='markdown',
            reply_markup=m.new_phonenumber_keyboard()
        )
    elif query.data == 'take_items_back_myself':
        text = 'Отлично мы ждем вас на нашем складе по адресу:' \
               f'\n*{db_handler.get_storage_address()}*\n' \
               f'Часы работы: *Пн-Вс* с *09:00-21:00*'
        query.edit_message_text(text=text, parse_mode='markdown')
    else:
        order_id = re.search(r'\d+', query.data).group()
        text = f'Вы собираетесь забрать заказ *№{order_id}*:\nВсе вещи ли частично?'
        query.edit_message_text(
            text=text,
            reply_markup=m.take_items_choice_keyboard(),
            parse_mode='markdown'
        )


def promt_update_customer_phone(update, context):
    text = "Введите номер телефона в формате *+7-XXX-XXX-XX-XX*\n" \
           "Если вы не увидите сообщение подтверждающее обновление телефона," \
           " попробуйте еще раз ввести в правильном формате"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='markdown')
    return 6


def write_new_customer_phone(update, context):
    text = update.message.text
    db_handler.add_phone_to_customer(context.user_data['user_id'], phone=text)
    update.message.reply_text('Отлично! Ваш номер обновлен. Наш курьер свяжется с вами\n'
                              'Хорошего Вам дня!')
