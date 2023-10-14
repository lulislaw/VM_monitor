from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import CallbackQuery
from keyboards import start_kb, vm_add_kb, sub_lst_kb
from settings.config import Config
from status_base import createdb, page, update_lst_page, get_user_status, update_user_status, add_user
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
    await bot.send_message(chat_id=message.chat.id,text='helloworld!', reply_markup=start_kb())


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def mail(message: types.Message):
    if message.text == "Добавить ВМ":
        await bot.send_message(chat_id=message.chat.id, text='vm_add_kb!', reply_markup=vm_add_kb())
    elif message.text == "Подписки ВМ":
        await bot.send_message(chat_id=message.chat.id, text="ZOV", reply_markup=sub_lst_kb(ip_addresses,
                                                                                                   message.chat.id))

@dp.callback_query_handler(text="next_page")
async def next_page_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id

    # Увеличиваем номер текущей страницы на 1
    update_lst_page(user_id, int(page(user_id)) + 1)

    # Обновляем сообщение с новой клавиатурой
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=sub_lst_kb(ip_addresses, user_id))

# Обработчик для кнопки "Назад"
@dp.callback_query_handler(text="prev_page")
async def prev_page_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id

    # Уменьшаем номер текущей страницы на 1
    update_lst_page(user_id, int(page(user_id)) - 1)

    # Обновляем сообщение с новой клавиатурой
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=sub_lst_kb(ip_addresses, user_id))

# @dp.message_handler(commands=['start', 'help'])
# async def mail(message: types.Message):
#     await bot.send_message(chat_id=message.chat.id, text='helloworld!', reply_markup=start_keyboard())
#
#
# @dp.message_handler(commands=['start', 'help'])
# async def mail(message: types.Message):
#     await bot.send_message(chat_id=message.chat.id, text='helloworld!', reply_markup=start_keyboard())
#
#
# @dp.message_handler(commands=['start', 'help'])
# async def mail(message: types.Message):
#     await bot.send_message(chat_id=message.chat.id, text='helloworld!', reply_markup=start_keyboard())
#


if __name__ == '__main__':
    executor.start_polling(dp)

