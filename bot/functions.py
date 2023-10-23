from db_main import get_user_page, get_server_record_by_ip, get_server_status


def sub_lst_text(lst: list, user_id, type_text='vm',ip_address = ''):
    if not lst:
        if type_text == 'vm':
            return "Вы не подписаны ни на одну виртуальную машину."
        elif type_text == 'notif':
            return "У этой машины не было уведомлений"
    page_size = 8
    current_page = get_user_page(user_id) - 1
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = lst[start_index:end_index]
    finish_text = ''
    if type_text == 'vm':
        for i, item in enumerate(current_lst):
            status = 'Запущена' if get_server_status(item) == 'success' else 'Выключена'
            finish_text = f'{finish_text}{(i + 1) + current_page * page_size}. {item}\t Статус: {status}\n'
    elif type_text == 'notif':
        finish_text = f'ip:{ip_address}\n'
        for i, item in enumerate(current_lst):
            finish_text = f'{finish_text}{(i + 1) + current_page * page_size}. ID: {item[0]} \tДата: {item[3]}'
            if item[1]:
                finish_text = f'{finish_text} \tТекст: {item[1][:64]}'
            if item[2]:
                finish_text = f'{finish_text} \tПрикреплен файл'
            finish_text = f'{finish_text} \n'
    return finish_text


def vm_info_func(ip_address):
    vm = get_server_record_by_ip(ip_address)
    status = 'Запущена' if get_server_status(ip_address) == 'success' else 'Выключена'
    return f"ip:{vm[1]}\nport:{vm[2]}\nusername:{vm[4]}\npassword:<span class='tg-spoiler'>{vm[5]}</span>\nlog_path:{vm[7]}\nСтатус: {status}"
