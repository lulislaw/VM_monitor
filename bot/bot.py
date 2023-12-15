from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import ChatActions
from aiogram.types import CallbackQuery
from keyboards import start_kb, vm_add_kb, sub_lst_kb, vm_info_kb, process_info_keyboard
from settings.config import Config
from functions import sub_lst_text, vm_info_func, process_info
from db_main import create_base, add_user_account, set_user_page, get_user_page, get_user_status, set_user_status, \
    create_server_first_time, get_user_ip, set_user_ip, set_port_server, set_password_server, set_username_server, \
    get_all_ip_addresses, subscription, get_subscription_status, get_subscribed_servers, get_subscribtion_table_by_ip, \
    add_notif, get_all_notify, get_notif_by_id, set_user_role, get_user_role, \
    get_server_record_by_ip, get_server_processes_by_ip, add_server_process, delete_process, set_timer_process, \
    get_process
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
config = Config()
bot = Bot(config.token)
dp = Dispatcher(bot)
create_base("create")


async def send_notify(chat_id_lst, ip_address, text='', log_file=''):
    add_notif(noti_text=text, data_path=log_file, date=datetime.now(), ip_server=ip_address)
    for chat_id in chat_id_lst:
        if log_file:
            with open(log_file, 'rb') as log_file_f:
                await bot.send_document(chat_id=chat_id, document=log_file_f, caption=f'{text}\n')
        elif text:
            await bot.send_message(chat_id=chat_id, text=text)


@dp.message_handler(commands=['start', 'help'])
async def mail(message: types.Message):
    add_user_account(id_tg=message.chat.id, name=message.from_user.full_name, status='start', lst_page=0)
    await bot.send_message(chat_id=message.chat.id, text='Мониторинг виртуальных машин',
                           reply_markup=start_kb(message.chat.id))


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    password = message.text.split(' ')[1]
    if password == config.admin_pass:
        set_user_role(tg_id=message.chat.id, role='admin')
        await bot.send_message(chat_id=message.chat.id,
                               text='Вы получили права администратора\n /admin user чтобы убрать права администратора',
                               reply_markup=start_kb(message.chat.id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    elif password == 'user':
        set_user_role(tg_id=message.chat.id, role='user')
        await bot.send_message(chat_id=message.chat.id, text='Вы убрали права администратора',
                               reply_markup=start_kb(message.chat.id))


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def action(message: types.Message):
    user_id = message.chat.id

    if message.text == "Подписки ВМ":
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
    elif message.text == "Поиск ВМ":
        await bot.send_message(chat_id=message.chat.id, text='Напишите ip-адрес виртуальной машины')
        set_user_status(tg_id=message.chat.id, status='search_ip')
    elif get_user_status(message.chat.id) == 'search_ip':
        set_user_status(message.chat.id, 'start')
        ip_address = message.text
        try:
            set_user_ip(message.chat.id, ip_address)
            sub = get_subscription_status(ip_address, user_id)
            await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id,
                                   text=vm_info_func(user_id, ip_address),
                                   reply_markup=vm_info_kb(user_id, sub))
        except Exception as e:
            await bot.send_message(chat_id=user_id, text='Виртуальной машины с таким ip нет!')
    elif get_user_role(user_id) == 'admin':
        if message.text == "Добавить ВМ":
            await bot.send_message(chat_id=message.chat.id, text='Напишите ip-адрес виртуальной машины')
            set_user_status(tg_id=message.chat.id, status='set_ip')
        elif get_user_status(message.chat.id) == 'set_ip':
            set_user_status(message.chat.id, 'start')
            ip_address = message.text
            set_user_ip(message.chat.id, ip_address)
            create_server_first_time(ip_address)
            await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id,
                                   text=vm_info_func(user_id, ip_address),
                                   reply_markup=vm_add_kb())
        elif get_user_status(message.chat.id) == 'set_port':
            set_user_status(message.chat.id, 'start')
            ip_address = get_user_ip(message.chat.id)
            set_port_server(ip_address, message.text)
            await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id,
                                   text=vm_info_func(user_id, ip_address),
                                   reply_markup=vm_add_kb())
        elif get_user_status(message.chat.id) == 'set_username':
            set_user_status(message.chat.id, 'start')
            ip_address = get_user_ip(message.chat.id)
            set_username_server(ip_address, message.text)
            await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id,
                                   text=vm_info_func(user_id, ip_address),
                                   reply_markup=vm_add_kb())
        elif get_user_status(message.chat.id) == 'set_password':
            set_user_status(message.chat.id, 'start')
            ip_address = get_user_ip(message.chat.id)
            set_password_server(ip_address, message.text)
            await bot.send_message(parse_mode=types.ParseMode.HTML, chat_id=message.chat.id,
                                   text=vm_info_func(user_id, ip_address),
                                   reply_markup=vm_add_kb())
        elif get_user_status(message.chat.id) == 'send_message':
            set_user_status(message.chat.id, 'start')
            ip_address = get_user_ip(message.chat.id)
            chat_id_lst = [array[2] for array in get_subscribtion_table_by_ip(ip_address) if array]
            unique_array = list(set(chat_id_lst))
            text_notif = f'Уведомление для ВМ({ip_address})\n{message.text}\n\n@{message.from_user.username}'
            await send_notify(chat_id_lst=unique_array, ip_address=ip_address, text=text_notif)

        elif get_user_status(message.chat.id) == 'cmd_command':
            if message.text == 'end':
                set_user_status(message.chat.id, 'start')
                await bot.send_message(chat_id=message.chat.id, text='cmd прекращена')
                return
            from monitoring import cmd_command
            ip_address = get_user_ip(message.chat.id)
            await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
            await bot.send_message(chat_id=message.chat.id, text=await cmd_command(ip_address, message.text))
        elif get_user_status(message.chat.id) == 'process_file':
            set_user_status(message.chat.id, 'start')
            ip_address = get_user_ip(message.chat.id)
            if '.' in message.text:
                add_server_process(ip_address, message.text)
            await bot.send_message(chat_id=user_id,
                                   text=sub_lst_text(get_server_processes_by_ip(ip_address), user_id,
                                                     type_text='process_file',
                                                     ip_address=ip_address),
                                   reply_markup=sub_lst_kb(get_server_processes_by_ip(ip_address), user_id,
                                                           'process_file'))
        elif get_user_status(message.chat.id) == 'set_timer':
            set_user_status(message.chat.id, 'start')
            id_process = get_user_ip(message.chat.id)
            ip_address = get_process(id_process)[1]
            timers = message.text.split(" ")
            timer = 10
            if timers:
                if timers[-1]:
                    timer = int(timers[-1])
                if len(timers) >= 2 and timers[-2]:
                    timer = int(timers[-2]) * 60 + timer
                if len(timers) >= 3 and timers[-3]:
                    timer = int(timers[-3]) * 3600 + timer
            if timer < 10: timer = 10
            if timer > 0:
                set_timer_process(id_process, new_time=timer)
                await bot.send_message(chat_id=user_id, text=process_info(id_process),
                                       reply_markup=process_info_keyboard(
                                           get_subscription_status(ip_address, user_id, id_process)))
            else:
                await bot.send_message(chat_id=user_id, text="Ошибка при изменение времени")
                await bot.send_message(chat_id=user_id, text=process_info(id_process),
                                       reply_markup=process_info_keyboard(
                                           get_subscription_status(ip_address, user_id, id_process)))


@dp.callback_query_handler(lambda c: c.data in ['prev', 'next'])
async def prev_page(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    if callback_query.data == 'prev':
        set_user_page(user_id, get_user_page(user_id) - 1)
    else:
        set_user_page(user_id, get_user_page(user_id) + 1)
    if callback_query.message.text.__contains__('Уведомления'):
        ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
        txt = sub_lst_text(get_all_notify(ip_address), callback_query.message.chat.id, type_text='notif',
                           ip_address=ip_address)
        rply_mrkp = sub_lst_kb(get_all_notify(ip_address), callback_query.message.chat.id, type_kb='notif')
    elif callback_query.message.text.__contains__('Процессы/Файлы'):
        ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
        txt = sub_lst_text(get_server_processes_by_ip(ip_address), user_id,
                           type_text='process_file',
                           ip_address=ip_address)
        rply_mrkp = sub_lst_kb(get_server_processes_by_ip(ip_address), user_id, 'process_file')
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
                                        reply_markup=vm_info_kb(user_id, sub))
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
    await bot.send_message(parse_mode=types.ParseMode.HTML, text=vm_info_func(user_id, ip_address), chat_id=user_id,
                           reply_markup=vm_info_kb(user_id, get_subscription_status(ip_address, user_id)))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('process_file_'))
async def vm_info(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    number = callback_query.data.split("process_file_")[1]
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    set_user_ip(user_id, ip_address)
    id_process = callback_query.message.text.split(f'{number}. ID: ')[1].split(' ')[0]
    if get_user_role(user_id) == "admin":
        await bot.send_message(chat_id=user_id, text=process_info(id_process),
                               reply_markup=process_info_keyboard(
                                   get_subscription_status(ip_address, user_id, id_process)))
    else:
        subscription(id_server=ip_address, id_user=user_id, process_file=id_process)
        await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                    text=sub_lst_text(get_server_processes_by_ip(ip_address), user_id,
                                                      type_text='process_file',
                                                      ip_address=ip_address))
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                            reply_markup=sub_lst_kb(get_server_processes_by_ip(ip_address), user_id,
                                                                    'process_file'))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('notif_'))
async def notif_info(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    number = callback_query.data.split("notif_")[1]
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    id_notif = callback_query.message.text.split(f'{number}. ID: ')[1].split(' ')[0]
    notif = get_notif_by_id(id_notif)
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
    await bot.edit_message_text(parse_mode=types.ParseMode.HTML, text=vm_info_func(user_id, ip_address),
                                chat_id=user_id,
                                message_id=callback_query.message.message_id)
    await bot.edit_message_reply_markup(chat_id=user_id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=vm_info_kb(user_id, get_subscription_status(ip_address, user_id)))
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
    if get_server_record_by_ip(ip_address)[5] == 'success':

        set_user_status(callback_query.message.chat.id, 'cmd_command')
        set_user_ip(callback_query.message.chat.id, ip_address)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=f'Пишите команды которые нужно выполнить на виртуальной машине({ip_address})\nДля прекращения cmd, напишите "end"\nВыполнение команд может занять некоторое время, не нужно спамить.')

    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text='Машина отключенна!')
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['process_files_vm'])
async def process_file(callback_query: CallbackQuery):
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    user_id = callback_query.message.chat.id
    await bot.send_message(chat_id=user_id,
                           text=sub_lst_text(get_server_processes_by_ip(ip_address), user_id, type_text='process_file',
                                             ip_address=ip_address),
                           reply_markup=sub_lst_kb(get_server_processes_by_ip(ip_address), user_id, 'process_file'))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['add_process'])
async def process_file(callback_query: CallbackQuery):
    if get_user_role(callback_query.message.chat.id) == 'admin':
        ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
        user_id = callback_query.message.chat.id
        set_user_status(user_id, 'process_file')
        set_user_ip(user_id, ip_address)
        await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                    text="Напишите процессы/файлы которые хотите добавить. Для файлов полный путь с именем файла, а для процессов полное имя\nНапример:\nC:/Users/admin/Desktop/log.log\nMsMpEng.exe")
    await callback_query.answer()



@dp.callback_query_handler(lambda c: c.data in ['process_delete'])
async def process_delete(callback_query: CallbackQuery):
    id_process = callback_query.message.text.split(f'ID: ')[1].split('\n')[0]
    delete_process(id_process)
    await callback_query.answer("Процесс удален!")
    ip_address = callback_query.message.text.split('ip: ')[1].split('\n')[0]
    user_id = callback_query.message.chat.id
    await bot.send_message(chat_id=user_id,
                           text=sub_lst_text(get_server_processes_by_ip(ip_address), user_id, type_text='process_file',
                                             ip_address=ip_address),
                           reply_markup=sub_lst_kb(get_server_processes_by_ip(ip_address), user_id, 'process_file'))
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['process_sub'])
async def process_sub(callback_query: CallbackQuery):
    ip_address = callback_query.message.text.split("ip: ")[1].split('\n')[0]
    user_id = callback_query.message.chat.id
    id_process = callback_query.message.text.split(f'ID: ')[1].split('\n')[0]
    subscription(id_server=ip_address, id_user=user_id, process_file=id_process)
    await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                text=process_info(id_process))
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=process_info_keyboard(
                                            get_subscription_status(ip_address, user_id, id_process)))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data in ['process_change_time'])
async def process_timer(callback_query: CallbackQuery):
    id_process = callback_query.message.text.split(f'ID: ')[1].split('\n')[0]
    user_id = callback_query.message.chat.id
    set_user_ip(user_id, id_process)
    set_user_status(user_id, "set_timer")
    await bot.send_message(chat_id=user_id,
                           text="Напишите с каким интервалом(в формате HH MM SS, через пробел) производить проверку этого процесса.")
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('edit_'))
async def vm_info(callback_query: CallbackQuery):
    ip_address = callback_query.message.text.split('ip:')[1].split('\n')[0]
    user_id = callback_query.message.chat.id
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
        await server_status(ip_address)
        await bot.edit_message_text(parse_mode=types.ParseMode.HTML, chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=vm_info_func(user_id, ip_address))
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=vm_info_kb(callback_query.message.chat.id,
                                                                    get_subscription_status(ip_address,
                                                                                            callback_query.message.chat.id)
                                                                    ))
        set_user_status(tg_id=callback_query.message.chat.id, status='start')
    elif callback_query.data == 'edit_vm':

        set_user_ip(user_id, ip_address)
        set_user_status(user_id, 'start')
        await bot.edit_message_text(parse_mode=types.ParseMode.HTML, chat_id=user_id,
                                    message_id=callback_query.message.message_id, text=vm_info_func(user_id, ip_address)
                                    )
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                            reply_markup=vm_add_kb())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
