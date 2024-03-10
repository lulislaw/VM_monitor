from db_main import get_user_page, get_server_record_by_ip, get_user_role, get_subscribtion_table_by_ip, get_process, \
    subscription, get_subscription_status


def service_message(text, vm, status):
    status = status.split('\n\n')[0]
    finish_text = f'ip: {vm[1]}\nos: {vm[7]}\nservice: {text}\n\nstatus:\n{status}'
    return finish_text


def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def sub_lst_text(lst: list, user_id, type_text='vm', ip_address=''):
    if not lst:
        if type_text == 'vm':
            return f"Здесь нет виртуальных машин."
        elif type_text == 'notif':
            return f"Уведомления\nip:{ip_address}\nУ этой машины не было уведомлений"
        elif type_text == 'process_file':
            return f"Процессы/Файлы\nip:{ip_address}\nНа данный момент нет процессов"

    page_size = 8
    current_page = get_user_page(user_id) - 1
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = lst[start_index:end_index]
    finish_text = ''
    if type_text == 'vm':
        for i, item in enumerate(current_lst):
            status = 'Запущена' if get_server_record_by_ip(item)[5] == 'success' else 'Выключена'
            finish_text = f'{finish_text}{(i + 1)}. {item}\t Статус: {status}\n'
    elif type_text == 'notif':
        finish_text = f'Уведомления\nip:{ip_address}\n'
        for i, item in enumerate(current_lst):
            finish_text = f'{finish_text}{(i + 1)}. ID: {item[0]} \tДата: {item[3]}'
            if item[1]:
                finish_text = f'{finish_text} \tТекст: {item[1][:64]}'
            if item[2]:
                finish_text = f'{finish_text} \tПрикреплен файл'
            finish_text = f'{finish_text} \n'
    elif type_text == 'process_file':
        finish_text = f'Процессы/Файлы\nip:{ip_address}\n'
        for i, item in enumerate(current_lst):
            finish_text = f'{finish_text}{(i + 1)}. ID: {item[0]}\t {item[2]}'
            if item[5] != None:
                finish_text = f'{finish_text}\t {item[5]}'
            if item[3] == 'process':
                status = 'Запущен' if item[4] == 'success' else 'Выключен'
                finish_text = f'{finish_text}\t | {status}'
            finish_text = f'{finish_text}\t | {get_subscription_status(id_server=ip_address, id_user=user_id, process_file=item[0])}'
            finish_text = f'{finish_text} \n'
    return finish_text


def vm_info_func(user_id, ip_address):
    vm = get_server_record_by_ip(ip_address)
    status = 'Запущена' if get_server_record_by_ip(ip_address)[5] == 'success' else 'Выключена'
    files = '0123'
    if get_user_role(user_id) == 'admin':
        return f"{vm[6]}\n{vm[7]}\nip:{vm[1]}\nport:{vm[2]}\nusername:{vm[3]}\npassword:<span class='tg-spoiler'>{vm[4]}</span>\nСтатус: {status}"
    return f"{vm[6]}\nip:{vm[1]}\nport:{vm[2]}\nСтатус: {status}"


def process_info(process_id):
    process = get_process(process_id)
    status = "Включен" if process[4] == "success" else "Выключен"
    timer = int(process[6])
    finish_time = seconds_to_hms(timer)
    return f"ID: {process[0]}\nip: {process[1]}\nПроцесс: {process[2]}\nСтатус: {status}\nОписание: {process[5]}\nВремя проверки: {finish_time}"
