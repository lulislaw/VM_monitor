from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import CallbackQuery
from keyboards import start_kb, vm_add_kb, sub_lst_kb, vm_info_kb
from settings.config import Config
from status_base import createdb, page, update_lst_page, get_user_status, update_user_status, add_user
from functions import sub_lst_text, vm_info_func
import logging

logging.basicConfig(level=logging.INFO)
config = Config()

bot = Bot(config.token)
dp = Dispatcher(bot)
createdb()

ip_addresses = [
    "192.168.0.1",
    "10.0.0.1",
    "172.16.0.1",
    "8.8.8.8",
    "127.0.0.1",
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
    "2606:2800:220:1:248:1893:25c8:1946",
    "192.168.0.1",
    "10.0.0.1",
    "172.16.0.1",
    "8.8.8.8",
    "127.0.0.1",
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
    "2606:2800:220:1:248:1893:25c8:1946",
    "192.168.0.1",
    "10.0.0.1",
    "172.16.0.1",
    "8.8.8.8",
    "127.0.0.1",
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
    "2606:2800:220:1:248:1893:25c8:1946",
    "::1"
]


@dp.message_handler(commands=['start', 'help'])
async def mail(message: types.Message):
    add_user(user_id=message.chat.id, user_status="start")
    await bot.send_message(chat_id=message.chat.id, text='helloworld!', reply_markup=start_kb())

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def action(message: types.Message):
    if message.text == "Добавить ВМ":
        await bot.send_message(chat_id=message.chat.id, text='vm_add_kb!', reply_markup=vm_add_kb())
    elif message.text == "Подписки ВМ":
        update_lst_page(message.chat.id, 1)
        await bot.send_message(chat_id=message.chat.id, text=sub_lst_text(ip_addresses, message.chat.id),
                               reply_markup=sub_lst_kb(ip_addresses,
                                                       message.chat.id))
    elif message.text == "Список ВМ":
        update_lst_page(message.chat.id, 1)
        # ИСПОЛЬЗОВАТЬ ДРУГОЙ СПИСОК ПОСЛЕ СОЗДАНИЯ БД
        await bot.send_message(chat_id=message.chat.id, text=sub_lst_text(ip_addresses, message.chat.id),
                               reply_markup=sub_lst_kb(ip_addresses,
                                                       message.chat.id))


@dp.callback_query_handler(lambda c: c.data in ['next'])
async def next_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    update_lst_page(user_id, page(user_id) + 1)
    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=sub_lst_text(ip_addresses, user_id))
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=sub_lst_kb(ip_addresses, user_id))

@dp.callback_query_handler(lambda c: c.data in ['prev'])
async def prev_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    update_lst_page(user_id, page(user_id) - 1)
    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=sub_lst_text(ip_addresses, user_id))
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=sub_lst_kb(ip_addresses, user_id))


# ИСПОЛЬЗОВАТЬ ДРУГОЙ СПИСОК ПОСЛЕ СОЗДАНИЯ БД
@dp.callback_query_handler(lambda c: c.data in ['sub_unsub'])
async def sub_unsub(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    await bot.send_message(text="ВМ инфо", chat_id=user_id)


# ИСПОЛЬЗОВАТЬ ДРУГОЙ СПИСОК ПОСЛЕ СОЗДАНИЯ БД
@dp.callback_query_handler(lambda c: c.data in ['notif'])
async def notif(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    await bot.send_message(text="ВМ инфо", chat_id=user_id)

@dp.callback_query_handler(lambda c: c.data.startswith('vm_'))
async def vm_info(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    await bot.send_message(parse_mode=types.ParseMode.HTML, text=vm_info_func(), chat_id=user_id,
        reply_markup=vm_info_kb())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
