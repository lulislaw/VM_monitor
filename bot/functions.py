
from db_main import get_user_page,get_server_record_by_ip


def sub_lst_text(lst: list, user_id):
    if not lst:
        return "Вы не подписаны ни на одну виртуальную машину."
    page_size = 8
    current_page = get_user_page(user_id) - 1
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = lst[start_index:end_index]
    finish_text = ''
    for i, item in enumerate(current_lst):
        finish_text = f'{finish_text}{(i + 1)+current_page*page_size}. {item}\n'
    return finish_text

def vm_info_func(ip_address):
    vm = get_server_record_by_ip(ip_address)
    return f"ip:{vm[1]}\nport:{vm[2]}\nusername:{vm[4]}\npassword:<span class='tg-spoiler'>{vm[5]}</span>"
