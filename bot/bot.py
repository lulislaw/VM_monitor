from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import ChatActions
from aiogram.types import CallbackQuery
from keyboards import start_kb, vm_add_kb, sub_lst_kb, vm_info_kb
from settings.config import Config
from functions import sub_lst_text, vm_info_func
from db_main import create_base, add_user_account, set_user_page, get_user_page, get_user_status, set_user_status, \
    create_server_first_time, get_user_ip, set_user_ip, set_port_server, set_password_server, set_username_server, \
    get_all_ip_addresses, subscription, get_subscription_status, get_subscribed_servers, get_subscribed_users, \
    add_notif, get_all_notify, get_notif_by_id, get_server_status,set_remote_path_server
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
config = Config()

bot = Bot(config.token)
dp = Dispatcher(bot)
create_base("create")


async def send_notify(chat_id, text='', log_file=''):
    if log_file:
        with open(log_file, 'rb') as log_file_f:
            await bot.send_document(chat_id=chat_id, document=log_file_f, caption=f'{text}\n')
    elif text:
        await bot.send_message(chat_id=chat_id, text=text)


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
        await bot.send_message(chat_id=message.chat.id,
                               text=sub_lst_text(get_subscribed_servers(message.chat.id), message.chat.id),
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
    elif get_user_status(message.chat.id) == 'set_remote_path':
        set_user_status(message.chat.id, 'start')
        ip_address = get_user_ip(message.chat.id)
        set_remote_path_server(ip_address,message.text)
        await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id, text=vm_info_func(ip_address),
                               reply_markup=vm_add_kb())
    elif get_user_status(message.chat.id) == 'send_message':
        set_user_status(message.chat.id, 'start')
        ip_address = get_user_ip(message.chat.id)
        add_notif(message.text, '', datetime.now(), ip_address)
        for user in get_subscribed_users(ip_address):
            if user != message.chat.id:
                await bot.send_message(chat_id=user, text=message.text)
    elif get_user_status(message.chat.id) == 'cmd_command':
        if message.text == 'end':
            set_user_status(message.chat.id, 'start')
            await bot.send_message(chat_id=message.chat.id, text='cmd прекращена')
            return
        from monitoring import cmd_command
        ip_address = get_user_ip(message.chat.id)
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)

        await bot.send_message(chat_id=message.chat.id, text=await cmd_command(ip_address, message.text))


@dp.callback_query_handler(lambda c: c.data in ['next'])
async def next_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    set_user_page(user_id, get_user_page(user_id) + 1)
    if callback_query.message.text.__contains__('ID'):
        ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
        txt = sub_lst_text(get_all_notify(ip_address), callback_query.message.chat.id, type_text='notif',
                           ip_address=ip_address)
        rply_mrkp = sub_lst_kb(get_all_notify(ip_address), callback_query.message.chat.id, type_kb='notif')
    else:
        txt = sub_lst_text(get_all_ip_addresses(), user_id)
        rply_mrkp = sub_lst_kb(get_all_ip_addresses(), user_id)

    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=txt)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=rply_mrkp)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['prev'])
async def prev_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    set_user_page(user_id, get_user_page(user_id) - 1)
    if callback_query.message.text.__contains__('ID'):
        ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
        txt = sub_lst_text(get_all_notify(ip_address), callback_query.message.chat.id, type_text='notif',
                           ip_address=ip_address)
        rply_mrkp = sub_lst_kb(get_all_notify(ip_address), callback_query.message.chat.id, type_kb='notif')
    else:
        txt = sub_lst_text(get_all_ip_addresses(), user_id)
        rply_mrkp = sub_lst_kb(get_all_ip_addresses(), user_id)

    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=txt)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=rply_mrkp)
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
    set_user_page(callback_query.message.chat.id, 1)
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    print(get_all_notify(ip_address))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=sub_lst_text(get_all_notify(ip_address),
                                             callback_query.message.chat.id, type_text='notif', ip_address=ip_address),
                           reply_markup=sub_lst_kb(get_all_notify(ip_address),
                                                   callback_query.message.chat.id, type_kb='notif'))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('vm_'))
async def vm_info(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    number = callback_query.data.split("vm_")[1]
    ip_address = callback_query.message.text.split(f'{number}. ')[1].split(' ')[0]
    set_user_ip(user_id, ip_address)
    await bot.send_message(parse_mode=types.ParseMode.HTML, text=vm_info_func(ip_address), chat_id=user_id,
                           reply_markup=vm_info_kb(get_subscription_status(ip_address, user_id)))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('notif_'))
async def notif_info(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    number = callback_query.data.split("notif_")[1]
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    notif = get_notif_by_id(number)
    if notif[2]:
        with open(notif[2], 'rb') as log_file_f:
            await bot.send_document(chat_id=user_id, document=log_file_f,
                                    caption=f'ip:{notif[4]}\nДата:{notif[3]}\n{notif[1]}')
    elif notif[1]:
        await bot.send_message(chat_id=user_id, text=f'ip:{notif[4]}\nДата:{notif[3]}\n{notif[1]}')
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['upd_status'])
async def update_status(callback_query: CallbackQuery):
    from monitoring import server_status
    user_id = callback_query.message.chat.id
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    await server_status(ip_address)
    await bot.edit_message_text(parse_mode=types.ParseMode.HTML, text=vm_info_func(ip_address), chat_id=user_id,
                                message_id=callback_query.message.message_id)
    await bot.edit_message_reply_markup(chat_id=user_id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=vm_info_kb(get_subscription_status(ip_address, user_id)))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['send_message'])
async def send_message(callback_query: CallbackQuery):
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    set_user_status(callback_query.message.chat.id, 'send_message')
    set_user_ip(callback_query.message.chat.id, ip_address)
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f'Напишите текст, который хотите отправить всем пользователям подписанным на эту машину({ip_address})')
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['cmd_command'])
async def send_cmd(callback_query: CallbackQuery):
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    if get_server_status(ip_address) == 'success':

        set_user_status(callback_query.message.chat.id, 'cmd_command')
        set_user_ip(callback_query.message.chat.id, ip_address)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=f'Пишите команды которые нужно выполнить на виртуальной машине({ip_address})\nДля прекращения cmd, напишите "end"\nВыполнение команд может занять некоторое время, не нужно спамить.')

    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text='Машина отключенна!')
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
        from monitoring import server_status
        ip_address = callback_query.message.text.split(f'ip:')[1].split('\n')[0]
        await server_status(ip_address)
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=callback_query.message.text)
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=vm_info_kb(
                                                get_subscription_status(ip_address,
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
    elif callback_query.data == 'edit_remote_path':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Напишите путь до файла на виртуальной машины\nПример:C:/Users/admin/log.log')
        set_user_status(tg_id=callback_query.message.chat.id, status='set_remote_path')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
