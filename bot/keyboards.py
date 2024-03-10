from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from db_main import get_user_page, get_user_role, get_user_ip, get_server_record_by_ip


def start_kb(user_id):
    pool_vm_button = KeyboardButton(text='Список ВМ')
    subs_vm_button = KeyboardButton(text='Подписки ВМ')
    add_vm_button = KeyboardButton(text='Добавить ВМ')
    search_vm_button = KeyboardButton(text='Поиск ВМ')
    if get_user_role(user_id) == 'admin':
        return ReplyKeyboardMarkup(row_width=3).add(pool_vm_button, subs_vm_button, add_vm_button)
    return ReplyKeyboardMarkup(row_width=3).add(pool_vm_button, subs_vm_button, search_vm_button)


def vm_add_kb():
    ip_bt = InlineKeyboardButton(text='Изменить ip', callback_data="edit_ip")
    port_bt = InlineKeyboardButton(text='Изменить port', callback_data="edit_port")
    username_bt = InlineKeyboardButton(text='Изменить учетную запись', callback_data="edit_username")
    password_bt = InlineKeyboardButton(text='Изменить пароль', callback_data="edit_password")

    accept_vm_add_bt = InlineKeyboardButton(text='Подтвердить', callback_data="edit_accept")

    return InlineKeyboardMarkup(row_width=2).add(ip_bt, port_bt, username_bt, password_bt,
                                                 accept_vm_add_bt)


def sub_lst_kb(lst: list, user_id, type_kb='vm'):
    page_size = 8
    current_page = get_user_page(user_id) - 1
    markup = InlineKeyboardMarkup(row_width=2)
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = list(range(start_index + 1, end_index + 1))
    while end_index > len(lst):
        current_lst.pop()
        end_index -= 1
    for i, item in enumerate(current_lst):
        markup.insert(InlineKeyboardButton(str(i + 1), callback_data=f'{type_kb}_{str(i + 1)}'))
    if current_page > 0:
        markup.insert(InlineKeyboardButton("Назад", callback_data='prev'))
    if end_index < len(lst):
        markup.insert(InlineKeyboardButton("Далее", callback_data='next'))
    if type_kb == "process_file":
        if get_user_role(user_id) == 'admin':
            markup.insert(InlineKeyboardButton("Добавить", callback_data='add_process'))
    return markup


def vm_info_kb(user_id, text_sub_bt):
    vm_sub_unsub = InlineKeyboardButton(text=text_sub_bt, callback_data="sub_unsub")
    vm_notif = InlineKeyboardButton(text='Уведомления', callback_data="notif")
    vm_status = InlineKeyboardButton(text='Проверить статус', callback_data="upd_status")
    vm_send = InlineKeyboardButton(text='Отправить сообщения', callback_data="send_message")
    vm_cmd = InlineKeyboardButton(text='cmd', callback_data="cmd_command")
    vm_process_files = InlineKeyboardButton(text='Процессы/Файлы', callback_data="process_files_vm")
    vm_edit_data = InlineKeyboardButton(text='Изменить', callback_data="edit_vm")
    vm_service = InlineKeyboardButton(text='Управление службами', callback_data="service")
    if get_user_role(user_id) == 'admin':
        if get_server_record_by_ip(get_user_ip(user_id))[7] == 'linux':
            return InlineKeyboardMarkup(row_width=2).add(vm_process_files, vm_sub_unsub, vm_cmd, vm_send, vm_status,
                                                         vm_notif, vm_service, vm_edit_data)
        else:
            return InlineKeyboardMarkup(row_width=2).add(vm_process_files, vm_sub_unsub, vm_cmd, vm_send, vm_status,
                                                         vm_notif, vm_edit_data)
    return InlineKeyboardMarkup(row_width=2).add(vm_process_files, vm_sub_unsub, vm_status, vm_notif)


def process_info_keyboard(sub_bt):
    process_sub_unsub = InlineKeyboardButton(text=sub_bt, callback_data="process_sub")
    process_delete = InlineKeyboardButton(text="Удалить", callback_data="process_delete")
    process_timer = InlineKeyboardButton(text="Изменить время проверки", callback_data="process_change_time")
    return InlineKeyboardMarkup(row_width=2).add(process_sub_unsub, process_delete, process_timer)


def service_keyboard():
    on_service = InlineKeyboardButton(text="Вкл", callback_data="ser_on")
    off_service = InlineKeyboardButton(text="Выкл", callback_data="ser_off")
    edit_service = InlineKeyboardButton(text="Выбрать другую", callback_data="ser_change")
    back_service = InlineKeyboardButton(text="Назад", callback_data="ser_back")
    return InlineKeyboardMarkup(row_width=2).add(on_service, off_service, edit_service, back_service)
