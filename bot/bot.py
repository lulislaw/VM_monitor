from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import CallbackQuery
from keyboards import start_kb, vm_add_kb, sub_lst_kb, vm_info_kb
from settings.config import Config

from functions import sub_lst_text, vm_info_func
from db_main import create_base, add_user_account, set_user_page, get_user_page, get_user_status, set_user_status, \
    create_server_first_time, get_user_ip, set_user_ip, set_port_server, set_password_server, set_username_server, \
    get_all_ip_addresses, subscription, get_subscription_status, get_subscribed_servers
import logging

logging.basicConfig(level=logging.INFO)
config = Config()

bot = Bot(config.token)
dp = Dispatcher(bot)
create_base("create")

async def send_notify(chat_id, text):
    with open(text, 'rb') as log_file:
        await bot.send_document(chat_id = chat_id, document=log_file, caption='Ваш лог файл')

@dp.message_handler(commands=['start', 'help'])
async def mail(message: types.Message):
    add_user_account(id_tg=message.chat.id, name=message.from_user.full_name, status='start', lst_page=0)
    await bot.send_message(chat_id=message.chat.id, text='Мониторинг виртуальных машин', reply_markup=start_kb())

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def action(message: types.Message):
    if message.text == "Добавить ВМ":

        await bot.send_message(chat_id=message.chat.id, text='Напишите ip-адрес виртуальной машины')
        set_user_status(tg_id=message.chat.id, status='set_ip')
    elif message.text == "Подписки ВМ":
        set_user_status(message.chat.id, 'start')
        set_user_page(message.chat.id, 1)
        await bot.send_message(chat_id=message.chat.id, text=sub_lst_text(get_subscribed_servers(message.chat.id), message.chat.id),
                               reply_markup=sub_lst_kb(get_subscribed_servers(message.chat.id),
                                                       message.chat.id))
    elif message.text == "Список ВМ":
        set_user_status(message.chat.id, 'start')
        set_user_page(message.chat.id, 1)
        await bot.send_message(chat_id=message.chat.id, text=sub_lst_text(get_all_ip_addresses(), message.chat.id),
                               reply_markup=sub_lst_kb(get_all_ip_addresses(),
                                                       message.chat.id))
    elif get_user_status(message.chat.id) == 'set_ip':
        set_user_status(message.chat.id, 'start')
        ip_address = message.text
        set_user_ip(message.chat.id, ip_address)
        create_server_first_time(ip_address)
        await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id, text=vm_info_func(ip_address),
                               reply_markup=vm_add_kb())
    elif get_user_status(message.chat.id) == 'set_port':
        set_user_status(message.chat.id, 'start')
        ip_address = get_user_ip(message.chat.id)
        set_port_server(ip_address, message.text)
        await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id, text=vm_info_func(ip_address),
                               reply_markup=vm_add_kb())
    elif get_user_status(message.chat.id) == 'set_username':
        set_user_status(message.chat.id, 'start')
        ip_address = get_user_ip(message.chat.id)
        set_username_server(ip_address, message.text)
        await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id, text=vm_info_func(ip_address),
                               reply_markup=vm_add_kb())
    elif get_user_status(message.chat.id) == 'set_password':
        set_user_status(message.chat.id, 'start')
        ip_address = get_user_ip(message.chat.id)
        set_password_server(ip_address, message.text)
        await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id, text=vm_info_func(ip_address),
                               reply_markup=vm_add_kb())


@dp.callback_query_handler(lambda c: c.data in ['next'])
async def next_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    set_user_page(user_id, get_user_page(user_id) + 1)
    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=sub_lst_text(get_all_ip_addresses(), user_id))
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=sub_lst_kb(get_all_ip_addresses(), user_id))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['prev'])
async def prev_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    set_user_page(user_id, get_user_page(user_id) - 1)
    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=sub_lst_text(get_all_ip_addresses(), user_id))
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=sub_lst_kb(get_all_ip_addresses(), user_id))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['sub_unsub'])
async def sub_unsub(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    sub = subscription(ip_address, user_id)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=vm_info_kb(sub))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['notif'])
async def notif(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    # show pool notif
    await bot.send_message(text="ВМ инфо", chat_id=user_id)


@dp.callback_query_handler(lambda c: c.data.startswith('vm_'))
async def vm_info(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    number = callback_query.data.split("vm_")[1]
    ip_address = callback_query.message.text.split(f'{number}. ')[1].split('\n')[0]
    set_user_ip(user_id, ip_address)
    await bot.send_message(parse_mode=types.ParseMode.HTML, text=vm_info_func(ip_address), chat_id=user_id,
                           reply_markup=vm_info_kb(get_subscription_status(ip_address, user_id)))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('edit_'))
async def vm_info(callback_query: CallbackQuery):
    if callback_query.data == 'edit_ip':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Напишите ip-адрес виртуальной машины')
        set_user_status(tg_id=callback_query.message.chat.id, status='set_ip')
    elif callback_query.data == 'edit_port':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Напишите порт виртуальной машины')
        set_user_status(tg_id=callback_query.message.chat.id, status='set_port')
    elif callback_query.data == 'edit_username':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Напишите учетную запись виртуальной машины')
        set_user_status(tg_id=callback_query.message.chat.id, status='set_username')
    elif callback_query.data == 'edit_password':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Напишите пароль учетной записи виртуальной машины')
        set_user_status(tg_id=callback_query.message.chat.id, status='set_password')
    elif callback_query.data == 'edit_accept':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=callback_query.message.text)
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=vm_info_kb(
                                                get_subscription_status(get_user_ip(callback_query.message.chat.id),
                                                                        callback_query.message.chat.id)
                                            ))
        set_user_status(tg_id=callback_query.message.chat.id, status='start')
    elif callback_query.data == 'edit_vm':
        user_id = callback_query.message.chat.id
        ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
        set_user_ip(user_id, ip_address)
        set_user_status(user_id, 'start')
        await bot.edit_message_text(parse_mode=types.ParseMode.HTML, chat_id=user_id,
                                    message_id=callback_query.message.message_id, text=vm_info_func(ip_address)
                                    )
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                            reply_markup=vm_add_kb())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
