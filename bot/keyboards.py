from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup

# списоук вм списоук подписок и добавить ещЙо

def start_keyboard():
    pool_vm_button = KeyboardButton(text='Список ВМ')
    subs_vm_button = KeyboardButton(text='Подпискм ВМ')
    add_vm_button = KeyboardButton(text='Добавить ВМ')

    return ReplyKeyboardMarkup(row_width=3).add(pool_vm_button,subs_vm_button,add_vm_button)
