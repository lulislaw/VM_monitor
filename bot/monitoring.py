import paramiko
import time
from db_main import get_server_record_by_ip, get_subscribtion_table_by_ip, get_all_ip_addresses, \
    set_server_status, get_ip_addresses_with_status, set_hostname_server, get_server_processes_by_ip, get_process, \
    set_process_status, set_process_last_check, set_os_server, get_latest_note
from datetime import datetime
import asyncio
from aiogram import exceptions
from rocketry import Rocketry

commands = {
    'linux': 'pgrep',
    'windows': 'tasklist | findstr /i'
}


def destroy_all_file():
    import os
    directory_path = "logs/"

    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Удален файл: {file_path}")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


destroy_all_file()
app = Rocketry(execution="async")


async def cmd_command(ip_address, command) -> str:
    vm = get_server_record_by_ip(ip_address)
    port = vm[2]
    username = vm[3]
    password = vm[4]
    try:
        if vm[7] == 'linux':
            command = f'echo "{password}" | sudo -S {command}'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)
        print(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            return output[:2048].strip()
        if error:
            return error[:2048]
        ssh.close()
    except paramiko.AuthenticationException:
        return 'Ошибка аутентификации. Проверьте имя пользователя и пароль.'
    except Exception as e:
        return f'Произошла ошибка: {e}'


async def get_cpu(vm):
    limit = 0.6
    cooldown = 120
    indextimer = 0
    current_time = datetime.now()
    textaboutload = 'Нагрузка на процессов за последние 1 минут свыше 90%!!!'
    if (vm[7] == 'windows'):
        print('win')
    elif (vm[7] == 'linux'):
        loads = (await cmd_command(vm[1], 'uptime')).split('load average: ')[1].split(', ')
        if float(loads[indextimer].replace(',', '.')) >= limit:
            note = get_latest_note(vm[1], textaboutload)
            if not note:
                return textaboutload
            time_object = datetime.strptime(note, "%Y-%m-%d %H:%M:%S.%f")
            time_difference = current_time - time_object
            if time_difference.total_seconds() > cooldown:
                return textaboutload
    return 0


async def server_status(ip_address):
    vm = get_server_record_by_ip(ip_address)
    port = vm[2]
    username = vm[3]
    password = vm[4]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    prev_status = vm[5]
    status = prev_status
    try:
        ssh.connect(ip_address, port, username, password)
        status = 'success'
        set_server_status(ip_address, status)
        if vm[6] == None:
            set_hostname_server(ip_address, await cmd_command(ip_address, 'hostname'))
        if vm[7] == None:
            os = await cmd_command(ip_address, 'ver')
            print('asdfasdfasdfasdf')
            print(os)
            if 'windows' in os.lower():
                set_os_server(ip_address, 'windows')
                print('windows')
            os = await cmd_command(ip_address, 'uname -a')
            if 'linux' in os.lower():
                set_os_server(ip_address, 'linux')
                print('linux')



    except paramiko.AuthenticationException:
        status = 'auth_error'
        set_server_status(ip_address, status)
    except paramiko.SSHException as e:
        status = 'ssh_error'
        set_server_status(ip_address, status)
    except paramiko.ssh_exception.NoValidConnectionsError:
        status = 'bad_connection'
        set_server_status(ip_address, status)
    except Exception as e:
        status = 'another_error'
        set_server_status(ip_address, status)
    finally:
        ssh.close()
        from bot import send_notify
        chat_id_lst = [item[2] for item in get_subscribtion_table_by_ip(ip_address) if
                       item[3] == None and item[4] == 'sub']
        if prev_status != 'success' and status == 'success':
            await send_notify(chat_id_lst=chat_id_lst, ip_address=ip_address,
                              text=f'{ip_address}\nМашина включилась')
        if prev_status == 'success' and status != 'success':
            await send_notify(chat_id_lst=chat_id_lst, ip_address=ip_address,
                              text=f'{ip_address}\nМашина отключилась')
        cpuload = await get_cpu(vm)
        if cpuload:
            await send_notify(chat_id_lst, ip_address, text=f'{ip_address}\n{cpuload}')


async def main_async(ip_address):
    from bot import send_notify
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    current_time = datetime.now().strftime("%M")
    try:
        vm = get_server_record_by_ip(ip_address)
        print(vm)
        port = vm[2]
        username = vm[3]
        password = vm[4]
        os = vm[7]
        print(os)
        ssh_client.connect(ip_address, port, username, password)
        remote_process_file = get_server_processes_by_ip(ip_address)
        current_datetime = datetime.now()
        total_seconds = current_datetime.timestamp()
        formatted_datetime = current_datetime.strftime("%y.%m.%d.%H.%M.%S")
        print(remote_process_file)
        print(total_seconds)

        for i, remote_pf in enumerate(remote_process_file):
            print(int(remote_pf[6]))
            print(int(remote_pf[7]))
            if total_seconds - int(remote_pf[6]) > int(remote_pf[7]):
                set_process_last_check(remote_pf[0], total_seconds)
                if remote_pf[3] == 'file':
                    chat_id_lst = [item[2] for item in get_subscribtion_table_by_ip(ip_address) if
                                   item[3] == str(remote_pf[0]) and item[4] == 'sub']
                    try:
                        sftp = ssh_client.open_sftp()
                        local_file_path = f'logs/file{i}_{ip_address}_{formatted_datetime}.log'
                        sftp.get(remote_pf[2], local_file_path)
                        await send_notify(chat_id_lst=chat_id_lst, ip_address=ip_address,
                                          text=f'Файл\n{ip_address}\n{remote_pf[2]}',
                                          log_file=local_file_path)
                        sftp.close()
                    except Exception as e:
                        await send_notify(chat_id_lst=chat_id_lst, ip_address=ip_address,
                                          text=f'{ip_address}\n\n{remote_pf[2]}\n\n{e}')
                elif remote_pf[3] == 'process':

                    chat_id_lst = [item[2] for item in get_subscribtion_table_by_ip(ip_address) if
                                   item[3] == str(remote_pf[0]) and item[4] == 'sub']
                    tasklist = await cmd_command(ip_address, f'{commands[os]} {remote_pf[2]}')
                    if tasklist != None:
                        set_process_status(ip_address, remote_pf[2], 'success')
                        if remote_pf[4] != 'success':
                            await send_notify(chat_id_lst, ip_address,
                                              text=f'ip:{ip_address}, процесс {remote_pf[2]} включился!')
                        set_process_status(ip_address, remote_pf[2], 'success')
                    else:
                        if remote_pf[4] == 'success':
                            await send_notify(chat_id_lst, ip_address,
                                              text=f'ip:{ip_address}, процесс {remote_pf[2]} отключен!')
                        set_process_status(ip_address, remote_pf[2], 'failure')


    except Exception as e:
        chat_id_lst = [item[2] for item in get_subscribtion_table_by_ip(ip_address) if
                       item[3] == None and item[4] == 'sub']
        await send_notify(chat_id_lst=chat_id_lst, ip_address=ip_address,
                          text=f'{ip_address}\n {e}')
    finally:
        ssh_client.close()


@app.task('every 10 seconds')
async def do_secondly():
    ip_addresses = get_all_ip_addresses()
    for address in ip_addresses:
        await server_status(address)
    ip_addresses_worked = get_ip_addresses_with_status()
    for address in ip_addresses_worked:
        await main_async(address)


async def main():
    rocketry_task = asyncio.create_task(app.serve())
    await rocketry_task


if __name__ == "__main__":
    asyncio.run(main())
