from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, create_engine, text, insert, select, cast, \
    update, delete
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import insert

engine = create_engine("sqlite+pysqlite:///database", echo=True)

metadata_obj = MetaData()
user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("status", String),
    Column("lst_page", Integer),
    Column("selected_ip", String),
    Column("role", String)
)

notification_table = Table(
    "notification",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("noti_text", String),
    Column("data_path", String),
    Column("date", String),
    Column("ip_server", ForeignKey("server.id"), nullable=False)
)

server_table = Table(
    "server",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("ip_address", String, unique=True),
    Column("port", String),
    Column("username", String),
    Column("password", String),
    Column("status", String),
    Column("hostname", String),
    Column("osystem", String)


)

subscription_table = Table(
    "subscription",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("id_server", ForeignKey("server.id"), nullable=False),
    Column("id_user", ForeignKey("user_account.id"), nullable=False),
    Column("process_file", String),
    Column("status_sub", String)
)

server_process_files_table = Table(
    "server_processes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("ip_address", String),
    Column("process_file", String),
    Column("type", String),
    Column("status", String),
    Column("description", String),
    Column("timer", Integer),
    Column("last_check", Integer)


)

# with engine.connect() as conn:
#     stmt = subscription_table.select().where(
#         (subscription_table.c.id_user == id_user) &
#         (subscription_table.c.status_sub == "sub") &
#         (subscription_table.c.process_file == None)
#     ).with_only_columns(subscription_table.c.id_server)

def get_latest_note(ip_address, liketext):
    stmt = (
        notification_table
        .select()
        .where(
            (notification_table.c.ip_server == ip_address) &
            (notification_table.c.noti_text.like(f'%{liketext}%'))
        )
        .order_by(notification_table.c.date.desc())
        .limit(1)
        .with_only_columns(notification_table.c.date)
    )

    with engine.connect() as conn:
        result = conn.execute(stmt)
        return result.scalar()

def delete_process(process_id):
    stmt = (
        delete(server_process_files_table).where(server_process_files_table.c.id == process_id)
    )
    stmt2 = (
        delete(subscription_table).where(subscription_table.c.process_file == process_id)
    )

    with engine.connect() as conn:
        conn.execute(stmt)
        conn.execute(stmt2)
        conn.commit()

    return 1


def set_process_last_check(id, time):
    stmt = (
        update(server_process_files_table)
        .where(
            (server_process_files_table.c.id == id)
        )
        .values(last_check=time)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def set_process_status(ip_address, process_file, status):
    stmt = (
        update(server_process_files_table)
        .where(
            (server_process_files_table.c.ip_address == ip_address) &
            (server_process_files_table.c.process_file == process_file)
        )
        .values(status=status)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def add_server_process(ip_address, process):
    if "\\" in process or "/" in process:
        type = 'file'
    else:
        type = 'process'
    with engine.connect() as conn:
        stmt = insert(server_process_files_table).values(
            ip_address=ip_address,
            process_file=process,
            type=type,
            status="None",
            timer=180,
            last_check=0
        )
        result = conn.execute(stmt)
        conn.commit()
    return result


def get_process(id, ip_address=None, process_file=None):
    with engine.connect() as conn:
        stmt = server_process_files_table.select().where(server_process_files_table.c.id == id)
        if ip_address != None:
            stmt = server_process_files_table.select().where(
                (server_process_files_table.c.ip_address == ip_address) &
                (server_process_files_table.c.process_file == process_file))
        result = conn.execute(stmt)
        row = result.fetchone()
        return row


def get_server_processes_by_ip(ip_address):
    with engine.connect() as conn:
        stmt = server_process_files_table.select().where(server_process_files_table.c.ip_address == ip_address)
        result = conn.execute(stmt)
        rows = result.fetchall()
        lst = []
        for row in rows:
            lst.append((row.id, row.ip_address, row.process_file, row.type, row.status, row.description, row.timer,
                        row.last_check))
        return lst


def subscription(id_server, id_user, process_file=None):
    with engine.connect() as conn:
        stmt_check = subscription_table.select().where(
            (subscription_table.c.id_server == id_server) &
            (subscription_table.c.id_user == id_user) &
            (subscription_table.c.process_file == process_file)
        )
        existing_record = conn.execute(stmt_check).fetchone()
        if existing_record is not None:
            current_status = existing_record.status_sub
            new_status = "sub" if current_status == "unsub" else "unsub"
            stmt_update = subscription_table.update().where(
                (subscription_table.c.id_server == id_server) &
                (subscription_table.c.id_user == id_user) &
                (subscription_table.c.process_file == process_file)
            ).values(status_sub=new_status)
            conn.execute(stmt_update)
            conn.commit()
            new_status_text = "Отписаться" if new_status == "sub" else "Подписаться"
            return new_status_text
        else:
            stmt_insert = subscription_table.insert().values(
                id_server=id_server,
                id_user=id_user,
                status_sub="sub",
                process_file=process_file
            )
            conn.execute(stmt_insert)
            conn.commit()
            return "Отписаться"


def get_subscribtion_table_by_ip(ip_address):
    with engine.connect() as conn:
        stmt = subscription_table.select().where(
            (subscription_table.c.id_server == ip_address) &
            (subscription_table.c.status_sub == "sub")
        )
        result = conn.execute(stmt)
        rows = result.fetchall()
        lst = []
        for row in rows:
            lst.append((row.id, row.id_server, row.id_user, row.process_file, row.status_sub))
        return lst


def get_subscribed_servers(id_user):
    with engine.connect() as conn:
        stmt = subscription_table.select().where(
            (subscription_table.c.id_user == id_user) &
            (subscription_table.c.status_sub == "sub") &
            (subscription_table.c.process_file == None)
        ).with_only_columns(subscription_table.c.id_server)
        result = conn.execute(stmt)
        id_servers = [row[0] for row in result.fetchall()]
        return id_servers


def get_all_notify(ip_address):
    with engine.connect() as conn:
        stmt = notification_table.select().where(
            (notification_table.c.ip_server == ip_address)
        )
        result = conn.execute(stmt)
        rows = result.fetchall().__reversed__()
        lst = []
        for row in rows:
            lst.append((row.id, row.noti_text, row.data_path, row.date, row.ip_server))

        return lst


def get_notif_by_id(id):
    with engine.connect() as conn:
        stmt = notification_table.select().where(
            (notification_table.c.id == id)
        )
        result = conn.execute(stmt)
        row = result.fetchone()
        return row


def add_notif(noti_text, data_path, date, ip_server):
    with engine.connect() as conn:
        stmt = insert(notification_table).values(
            noti_text=noti_text,
            data_path=data_path,
            date=date,
            ip_server=ip_server
        )
        result = conn.execute(stmt)
        conn.commit()
    return result


def get_ip_addresses_with_status(status='success'):
    with engine.connect() as conn:
        stmt = select(server_table.c.ip_address).where(server_table.c.status == status)
        result = conn.execute(stmt)
        ip_addresses = [row[0] for row in result.fetchall()]
        return ip_addresses


def get_all_ip_addresses():
    with engine.connect() as conn:
        stmt = select(server_table.c.ip_address)
        result = conn.execute(stmt)
        ip_addresses = [row[0] for row in result.fetchall()]
        return ip_addresses


def create_server_first_time(ip_address):
    with engine.connect() as conn:
        stmt = insert(server_table).values(ip_address=ip_address)
        stmt = stmt.on_conflict_do_nothing(index_elements=[server_table.c.ip_address])
        result = conn.execute(stmt)
        conn.commit()


def set_timer_process(process_id, new_time):
    with engine.connect() as conn:
        stmt = server_process_files_table.update().where(server_process_files_table.c.id == process_id).values(
            timer=new_time)
        conn.execute(stmt)
        conn.commit()


def set_port_server(ip_address, new_port):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(port=new_port)
        result = conn.execute(stmt)
        conn.commit()

def set_os_server(ip_address, new_os):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(osystem=new_os)
        result = conn.execute(stmt)
        conn.commit()


def set_hostname_server(ip_address, hostname):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(hostname=hostname)
        result = conn.execute(stmt)
        conn.commit()


def set_username_server(ip_address, username):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(username=username)
        result = conn.execute(stmt)
        conn.commit()


def set_port_server(ip_address, port):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(port=port)
        result = conn.execute(stmt)
        conn.commit()


def set_username_server(ip_address, new_username):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(username=new_username)
        result = conn.execute(stmt)
        conn.commit()


def set_password_server(ip_address, new_password):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(password=new_password)
        result = conn.execute(stmt)
        conn.commit()


def get_server_record_by_ip(ip_address):
    with engine.connect() as conn:
        stmt = server_table.select().where(server_table.c.ip_address == ip_address)
        result = conn.execute(stmt)
        record = result.fetchone()
        print(record)
        return record


def get_subscription_status(id_server, id_user, process_file=None):
    with engine.connect() as conn:
        stmt = subscription_table.select().where(
            (subscription_table.c.id_server == id_server) &
            (subscription_table.c.id_user == id_user) &
            (subscription_table.c.process_file == process_file)
        )
        result = conn.execute(stmt)
        record = result.fetchone()
        if record:
            new_status_text = "Отписаться" if record.status_sub == "sub" else "Подписаться"
            return new_status_text
        else:
            return "Подписаться"


def add_user_account(id_tg, name, status, lst_page):
    with engine.connect() as conn:
        stmt = insert(user_table).values(
            id=id_tg,
            name=name,
            status=status,
            lst_page=lst_page,
            selected_ip="",
            role="user"
        ).on_conflict_do_update(
            index_elements=[user_table.c.id],
            set_={
                "name": name,
                "status": status,
                "lst_page": lst_page,
                "selected_ip": ""
            }
        )
        result = conn.execute(stmt)
        conn.commit()
    return result


def create_base(action):  # 'drop' - del , 'create'
    if action == 'create':
        metadata_obj.create_all(engine)
    if action == 'drop':
        metadata_obj.drop_all(engine)


def set_server_status(ip, status):
    stmt = (
        update(server_table)
        .where(server_table.c.ip_address == ip)
        .values(status=status)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def set_subs_status(server_id, user_id, status):
    stmt = (
        update(server_table)
        .where(server_table.c.id_server == server_id and server_table.c.id_user == user_id)
        .values(status_sub=status)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def set_user_page(tg_id, page):
    stmt = (
        update(user_table)
        .where(user_table.c.id == tg_id)
        .values(lst_page=page)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def set_user_role(tg_id, role):
    stmt = (
        update(user_table)
        .where(user_table.c.id == tg_id)
        .values(role=role)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def get_tables_keys(table):
    print(table.c.keys())
    return


def get_user_status(tg_id):
    stmt = select(cast(user_table.c.status, String)).where(user_table.c.id == tg_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        if result:
            for row in result:
                print(row[0])
                return row[0]


def set_user_status(tg_id, status):
    stmt = (
        update(user_table)
        .where(user_table.c.id == tg_id)
        .values(status=status)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def get_user_ip(tg_id):
    stmt = select(cast(user_table.c.selected_ip, String)).where(user_table.c.id == tg_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        if result:
            for row in result:
                print(row[0])
                return row[0]


def set_user_ip(tg_id, ip):
    stmt = (
        update(user_table)
        .where(user_table.c.id == tg_id)
        .values(selected_ip=ip)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return result


def get_user_page(tg_id):
    stmt = select(cast(user_table.c.lst_page, String)).where(user_table.c.id == tg_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        if result:
            for row in result:
                return int(row[0])


def get_user_role(tg_id):
    stmt = select(cast(user_table.c.role, String)).where(user_table.c.id == tg_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        if result:
            for row in result:
                return (row[0])


def get_sub_status(server_id, user_id):
    stmt = select(cast(subscription_table.c.status, String)).where(
        subscription_table.c.id_server == server_id and subscription_table.c.id_user == user_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            print(row[0])

    return


def add_data(table_name, collumn_one, data_one, collumn_two, data_two, collumn_three, data_three, collumn_four,
             data_four, collumn_five, data_five):
    with engine.connect() as conn:
        result = conn.execute(
            insert(table_name),
            [
                {collumn_one: data_one, collumn_two: data_two, collumn_three: data_three, collumn_four: data_four,
                 collumn_five: data_five},
            ],
        )
        conn.commit()

    return result
