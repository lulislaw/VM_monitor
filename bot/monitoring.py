import paramiko
import time
from db_main import get_server_record_by_ip, get_subscribed_users, get_all_ip_addresses, get_server_status, \
    set_server_status, get_ip_addresses_with_status,add_notif
from datetime import datetime
import asyncio
from aiogram import exceptions
from rocketry import Rocketry

app = Rocketry(execution="async")


async def cmd_command(ip_address, command) -> str:
    vm = get_server_record_by_ip(ip_address)
    port = vm[2]
    username = vm[4]
    password = vm[5]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)
        print(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            return output[:2048]
        if error:
            return error[:2048]
        ssh.close()
    except paramiko.AuthenticationException:
        return 'Ошибка аутентификации. Проверьте имя пользователя и пароль.'
    except Exception as e:
        return f'Произошла ошибка: {e}'


async def server_status(ip_address):
    vm = get_server_record_by_ip(ip_address)
    port = vm[2]
    username = vm[4]
    password = vm[5]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    prev_status = get_server_status(ip_address)
    status = prev_status
    try:
        ssh.connect(ip_address, port, username, password)
        status = 'success'
        set_server_status(ip_address, status)
        # print('SSH-подключение успешно установлено')
    except paramiko.AuthenticationException:
        status = 'auth_error'
        set_server_status(ip_address, status)
        # print('Ошибка аутентификации. Проверьте имя пользователя и пароль.')
    except paramiko.SSHException as e:
        status = 'ssh_error'
        set_server_status(ip_address, status)
        # print(f'Ошибка SSH: {e}')
    except paramiko.ssh_exception.NoValidConnectionsError:
        status = 'bad_connection'
        set_server_status(ip_address, status)
        # print('Не удается установить соединение. Проверьте хост или порт.')
    except Exception as e:
        status = 'another_error'
        set_server_status(ip_address, status)
        # print(f'Произошла ошибка: {e}')
    finally:
        ssh.close()
        if prev_status == 'success' and status != 'success':
            from bot import send_notify
            add_notif('Машина отключилась','',f'{datetime.now()}',ip_address)
            for user in get_subscribed_users(ip_address):
                await send_notify(chat_id=user, text=f'{ip_address}\nМашина отключилась')


async def main_async(ip_address):
    from bot import send_notify
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        vm = get_server_record_by_ip(ip_address)
        print(vm)
        port = vm[2]
        username = vm[4]
        password = vm[5]
        ssh_client.connect(ip_address, port, username, password)
        sftp = ssh_client.open_sftp()
        remote_file_path = vm[7]
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%y.%m.%d.%H.%M.%S")
        local_file_path = f'logs/log_{ip_address}_{formatted_datetime}.log'
        sftp.get(remote_file_path, local_file_path)
        sftp.close()
        add_notif('',local_file_path,current_datetime,ip_address)
        for user in get_subscribed_users(ip_address):
            await send_notify(chat_id=user, log_file=local_file_path, text=current_datetime)
    except Exception as e:
        add_notif(e, '', datetime.now(), ip_address)
        for user in get_subscribed_users(ip_address):
            await send_notify(chat_id=user, text=f'{ip_address}\n {e}')
    finally:
        ssh_client.close()


@app.task('every 1 minute')
async def do_minutely():
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
