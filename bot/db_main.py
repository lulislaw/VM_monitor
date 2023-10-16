from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, create_engine, text, insert, select, cast, \
    update
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
)

# ////

notification_table = Table(
    "notification",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("noti_text", String),
    Column("data_path", String),
    Column("date", String),
    Column("id_server", ForeignKey("server.id"), nullable=False)
)

# ////

server_table = Table(
    "server",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("ip_address", String, unique=True),
    Column("port", String),
    Column("name", String),
    Column("username", String),
    Column("password", String),
    Column("status", String)
)

# ////

subscription_table = Table(
    "subscription",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("id_server", ForeignKey("server.id"), nullable=False),
    Column("id_user", ForeignKey("user_account.id"), nullable=False),
    Column("status_sub", String)
)


def get_subscribed_users(ip_address):
    with engine.connect() as conn:
        stmt = subscription_table.select().where(
            (subscription_table.c.id_server == ip_address) &
            (subscription_table.c.status_sub == "sub")
        ).with_only_columns(subscription_table.c.id_user)
        result = conn.execute(stmt)
        id_users = [row[0] for row in result.fetchall()]
        return id_users
def get_subscribed_servers(id_user):
    with engine.connect() as conn:
        stmt = subscription_table.select().where(
            (subscription_table.c.id_user == id_user) &
            (subscription_table.c.status_sub == "sub")
        ).with_only_columns(subscription_table.c.id_server)
        result = conn.execute(stmt)
        id_servers = [row[0] for row in result.fetchall()]
        return id_servers



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


def set_port_server(ip_address, new_port):
    with engine.connect() as conn:
        stmt = server_table.update().where(server_table.c.ip_address == ip_address).values(port=new_port)
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

def get_subscription_status(id_server, id_user):
    with engine.connect() as conn:
        stmt = subscription_table.select().where(
            (subscription_table.c.id_server == id_server) &
            (subscription_table.c.id_user == id_user)
        )
        result = conn.execute(stmt)
        record = result.fetchone()
        if record:
            new_status_text = "Отписаться" if record.status_sub == "sub" else "Подписаться"
            return new_status_text
        else:
            return "Подписаться"

def subscription(id_server, id_user):
    with engine.connect() as conn:
        stmt_check = subscription_table.select().where(
            (subscription_table.c.id_server == id_server) &
            (subscription_table.c.id_user == id_user)
        )
        existing_record = conn.execute(stmt_check).fetchone()
        if existing_record is not None:
            current_status = existing_record.status_sub
            new_status = "sub" if current_status == "unsub" else "unsub"
            stmt_update = subscription_table.update().where(
                (subscription_table.c.id_server == id_server) &
                (subscription_table.c.id_user == id_user)
            ).values(status_sub=new_status)
            conn.execute(stmt_update)
            conn.commit()
            new_status_text = "Отписаться" if new_status == "sub" else "Подписаться"
            return new_status_text
        else:
            stmt_insert = subscription_table.insert().values(
                id_server=id_server,
                id_user=id_user,
                status_sub="sub"
            )
            conn.execute(stmt_insert)
            conn.commit()
            return "Отписаться"



def add_user_account(id_tg, name, status, lst_page):
    with engine.connect() as conn:
        stmt = insert(user_table).values(
            id=id_tg,
            name=name,
            status=status,
            lst_page=lst_page,
            selected_ip=""
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


def create_base(action):  # 'drop' чтобы удалить, 'create' чтобы создать
    if action == 'create':
        metadata_obj.create_all(engine)
    if action == 'drop':
        metadata_obj.drop_all(engine)


def set_server_status(server_name, status):
    stmt = (
        update(server_table)
        .where(server_table.c.name == server_name)
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


def get_tables_keys(table):
    print(table.c.keys())
    return


def get_server_status(server_name):
    stmt = select(cast(server_table.c.status, String)).where(server_table.c.name == server_name)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            print(row[0])

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
