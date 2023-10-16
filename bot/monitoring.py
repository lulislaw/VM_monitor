import paramiko
import time
from db_main import get_server_record_by_ip, get_subscribed_users, get_all_ip_addresses
from bot import send_notify
import asyncio
from rocketry import Rocketry


app = Rocketry(execution="async")
async def main_async(ip_address):
    vm = get_server_record_by_ip(ip_address)
    print(vm)
    port = vm[2]
    username = vm[4]
    password = vm[5]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(ip_address, port, username, password)
        sftp = ssh_client.open_sftp()
        remote_file_path = 'C:/Users/admin/log.log'
        local_file_path = f'log_{ip_address}.log'
        sftp.get(remote_file_path, local_file_path)
        sftp.close()
        for user in get_subscribed_users(ip_address):
            await send_notify(user,local_file_path)
    finally:
        ssh_client.close()


@app.task('every 1 minute')
async def do_minutely():
    ip_addresses = get_all_ip_addresses()
    for address in ip_addresses:
        await main_async(address)
async def main():
    rocketry_task = asyncio.create_task(app.serve())
    await rocketry_task

if __name__ == "__main__":
    asyncio.run(main())