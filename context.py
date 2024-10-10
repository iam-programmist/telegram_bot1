import psycopg2
from secret import database_password
def open_connection():
    conn = psycopg2.connect(
        database = "Telegrambot",
        host = "localhost",
        user = "postgres",
        password = database_password,
        port = 5432
    )
    return conn
def close_connection(conn, cur):
    cur.close()
    conn.close()
def create_database_tables():
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("""create table if not exists users(
                user_id serial primary key,
                username varchar(50) unique not null,
                password varchar(50) not null,
                first_name varchar(50),
                last_name varchar(50),
                is_active boolean default false);
                """)
    conn.commit()
    close_connection(conn, cur)
