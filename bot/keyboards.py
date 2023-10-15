from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from status_base import page, update_lst_page





def start_kb():
    pool_vm_button = KeyboardButton(text='Список ВМ')
    subs_vm_button = KeyboardButton(text='Подписки ВМ')
    add_vm_button = KeyboardButton(text='Добавить ВМ')

    return ReplyKeyboardMarkup(row_width=3).add(pool_vm_button, subs_vm_button, add_vm_button)


def vm_add_kb():
    ip_bt = InlineKeyboardButton(text='ip_bt', callback_data="1")
    port_bt = InlineKeyboardButton(text='port_bt', callback_data="2")
    username_bt = InlineKeyboardButton(text='username_bt', callback_data="3")
    password_bt = InlineKeyboardButton(text='password_bt', callback_data="4")
    accept_vm_add_bt = InlineKeyboardButton(text='accept_vm_add_bt', callback_data="5")

    return InlineKeyboardMarkup(row_width=2).add(ip_bt, port_bt, username_bt, password_bt, accept_vm_add_bt)


def sub_lst_kb(lst: list, user_id):
    page_size = 8
    current_page = page(user_id) - 1
    markup = InlineKeyboardMarkup(row_width=2)
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = list(range(start_index + 1, end_index + 1))
    while end_index > len(lst):
        current_lst.pop()
        end_index -= 1
    for item in current_lst:
        markup.insert(InlineKeyboardButton(str(item), callback_data=f'vm_{str(item)}'))
    if current_page > 0:
        markup.insert(InlineKeyboardButton("Назад", callback_data='prev'))
    if end_index < len(lst):
        markup.insert(InlineKeyboardButton("Далее", callback_data='next'))
    return markup


def vm_info_kb():
    vm_sub_unsub = InlineKeyboardButton(text='Подписаться', callback_data="sub_unsub")
    vm_notif = InlineKeyboardButton(text='Уведомления', callback_data="notif")

    return InlineKeyboardMarkup(row_width=2).add(vm_sub_unsub, vm_notif)