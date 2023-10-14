from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from status_base import page, update_lst_page
# списоук вм списоук подписок и добавить ещЙо


def start_kb():
    pool_vm_button = KeyboardButton(text='Список ВМ')
    subs_vm_button = KeyboardButton(text='Подписки ВМ')
    add_vm_button = KeyboardButton(text='Добавить ВМ')

    return ReplyKeyboardMarkup(row_width=3).add(pool_vm_button,subs_vm_button,add_vm_button)

def vm_add_kb():
    ip_bt = InlineKeyboardButton(text='ip_bt', callback_data="1")
    port_bt = InlineKeyboardButton(text='port_bt', callback_data="2")
    username_bt = InlineKeyboardButton(text='username_bt', callback_data="3")
    password_bt = InlineKeyboardButton(text='password_bt', callback_data="4")
    accept_vm_add_bt = InlineKeyboardButton(text='accept_vm_add_bt', callback_data="5")

    return InlineKeyboardMarkup(row_width=2).add(ip_bt, port_bt, username_bt, password_bt, accept_vm_add_bt)

def create_reply_keyboard(lst_titles, symbol=''):
    num_buttons = len(lst_titles)
    MAX_BUTTONS_PER_ROW = 4
    num_cols = min(num_buttons, MAX_BUTTONS_PER_ROW)
    num_rows = (num_buttons + num_cols - 1) // num_cols
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(num_rows):
        row_buttons = []
        for j in range(num_cols):
            button_index = i * num_cols + j
            if button_index >= num_buttons:
                break
            button_text = f"{symbol}{lst_titles[button_index]}"
            button_callback = f"account_button"
            row_buttons.append(InlineKeyboardButton(button_text, callback_data=button_callback))
        keyboard.row(*row_buttons)

    return keyboard

# def sub_lst_kb(lst: list, user_id):
#     vm_list_length = len(lst)
#     if page(user_id) == None:
#         update_lst_page(user_id, 1)
#     if vm_list_length < 10:
#         return create_reply_keyboard(lst)
def sub_lst_kb(lst: list, user_id):
    vm_list_length = len(lst)
    current_page = page(user_id) if page(user_id) != 0 else 1

    # Количество элементов на одной странице
    items_per_page = 7

    # Вычисляем начало и конец текущей страницы
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, vm_list_length)

    # Создаем клавиатуру для текущей страницы
    keyboard = create_reply_keyboard(lst[start_idx:end_idx])

    # Добавляем кнопки "Назад" и "Дальше" при необходимости
    if current_page > 1:
        keyboard.row(InlineKeyboardButton('Назад', callback_data='prev_page'))
    if end_idx < vm_list_length:
        keyboard.row(InlineKeyboardButton('Дальше', callback_data='next_page'))

    return keyboard
def start_keyboard():
    pool_vm_button = InlineKeyboardButton(text='Список ВМ')
    subs_vm_button = InlineKeyboardButton(text='Подпискм ВМ')
    add_vm_button = InlineKeyboardButton(text='Добавить ВМ')

    return InlineKeyboardMarkup(row_width=3).add(pool_vm_button,subs_vm_button,add_vm_button)

def start_keyboard():
    pool_vm_button = InlineKeyboardButton(text='Список ВМ')
    subs_vm_button = InlineKeyboardButton(text='Подпискм ВМ')
    add_vm_button = InlineKeyboardButton(text='Добавить ВМ')

    return InlineKeyboardMarkup(row_width=3).add(pool_vm_button,subs_vm_button,add_vm_button)