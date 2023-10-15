from status_base import page

vm = ('192.168.0.100', '22', 'SERV2', 'admin', 'abc123')

def sub_lst_text(lst: list, user_id):
    page_size = 8
    current_page = page(user_id) - 1
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = lst[start_index:end_index]
    finish_text = ''
    for i, item in enumerate(current_lst):
        finish_text = f'{finish_text}{(i + 1)+current_page*page_size}. {item}\n'
    return finish_text

def vm_info_func(vm = vm):
    return f"ip:{vm[0]}\nport:{vm[1]}\nhostname:{vm[2]}\nname:{vm[3]}\npassword:<span class='tg-spoiler'>{vm[4]}</span>"
