from status_base import page
def sub_lst_text(lst: list, user_id):
    page_size = 7
    current_page = page(user_id) - 1
    start_index = current_page * page_size
    end_index = (current_page + 1) * page_size
    current_lst = lst[start_index:end_index]
    finish_text = ''
    for i, item in enumerate(current_lst):
        finish_text = f'{finish_text}{(i + 1)+current_page*page_size}. {item}\n'
    return finish_text