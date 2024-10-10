import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from secret import *
from context import *
bot = telebot.TeleBot(api_key, parse_mode=None)
create_database_tables()

def registration(username, password, first_name, last_name, chat_id):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute(f"select * from users where username = '{username}'")
    if cur.fetchone():
        bot.send_message(chat_id, "Имя пользователя уже занято.")
    else:
        cur.execute(f"insert into users (username, password, first_name, last_name) values ('{username}', '{password}', '{first_name}', '{last_name}')")
        conn.commit()
        bot.send_message(chat_id, "Регистрация прошла успешно.")
    close_connection(conn, cur)

def login(username, password, chat_id):
    conn = open_connection()
    cur = conn.cursor()    
    cur.execute(f"select * from users where username = '{username}' and password = '{password}'")
    user = cur.fetchone()
    if user:
        cur.execute(f"update users set is_active = true where username = '{username}'")
        conn.commit()
        bot.send_message(chat_id, "Вы успешно вошли в систему.")
    else:
        bot.send_message(chat_id, "Неверное имя пользователя или пароль.")
    close_connection(conn, cur)

def logout(username, chat_id):
    conn = open_connection()
    cur = conn.cursor()    
    cur.execute(f"update users set is_active = false where username = '{username}'")
    conn.commit()
    close_connection(conn, cur)
    bot.send_message(chat_id, "Вы успешно вышли из системы.")

def update_user_data(username, chat_id, first_name=None, last_name=None):
    conn = open_connection()
    cur = conn.cursor()
    if first_name:
        cur.execute(f"update users set first_name = '{first_name}' where username = '{username}'")
    if last_name:
        cur.execute(f"update users set last_name = '{last_name}' where username = '{username}'")
    conn.commit()
    close_connection(conn, cur)
    bot.send_message(chat_id, "Ваши данные были обновлены.")

def get_user_by_username(username):
    conn = open_connection()
    cur = conn.cursor()    
    cur.execute(f"select * from users where username = '{username}'")
    user = cur.fetchone()
    close_connection(conn, cur)
    return user

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = KeyboardButton("Регистрация")
    button2 = KeyboardButton("Вход")
    button3 = KeyboardButton("Выход")
    button4 = KeyboardButton("Обновить данные")
    button5 = KeyboardButton("Показать данные пользователя")
    markup.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id, "Добро пожаловать в бот.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def main_menu(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if text == "регистрация":
        bot.send_message(chat_id, "Введите ваш username:")
        bot.register_next_step_handler(message, registration_username)
    elif text == "вход":
        bot.send_message(chat_id, "Введите ваш username:")
        bot.register_next_step_handler(message, login_username)
    elif text == "выход":
        bot.send_message(chat_id, "Введите ваш username для выхода:")
        bot.register_next_step_handler(message, logout_username)
    elif text == "обновить данные":
        bot.send_message(chat_id, "Введите ваш username для обновления данных:")
        bot.register_next_step_handler(message, update_username)
    elif text == "показать данные пользователя":
        bot.send_message(chat_id, "Введите username для поиска:")
        bot.register_next_step_handler(message, get_user_info)
    else:
        bot.send_message(chat_id, "Команда не распознана. Попробуйте ещё раз.")

def registration_username(message):
    username = message.text
    bot.send_message(message.chat.id, "Введите ваш пароль:")
    bot.register_next_step_handler(message, registration_password, username)

def registration_password(message, username):
    password = message.text
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, registration_firstname, username, password)

def registration_firstname(message, username, password):
    first_name = message.text
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, registration_lastname, username, password, first_name)

def registration_lastname(message, username, password, first_name):
    last_name = message.text
    chat_id = message.chat.id
    registration(username, password, first_name, last_name, chat_id)

def login_username(message):
    username = message.text
    bot.send_message(message.chat.id, "Введите ваш пароль:")
    bot.register_next_step_handler(message, login_password, username)

def login_password(message, username):
    password = message.text
    chat_id = message.chat.id
    login(username, password, chat_id)

def logout_username(message):
    username = message.text
    chat_id = message.chat.id
    logout(username, chat_id)

def update_username(message):
    username = message.text
    bot.send_message(message.chat.id, "Введите новое имя:")
    bot.register_next_step_handler(message, update_firstname, username)

def update_firstname(message, username):
    first_name = message.text
    bot.send_message(message.chat.id, "Введите новую фамилию (или оставьте пустым):")
    bot.register_next_step_handler(message, update_lastname, username, first_name)

def update_lastname(message, username, first_name):
    last_name = message.text
    chat_id = message.chat.id
    update_user_data(username, chat_id, first_name, last_name if last_name else None)

def get_user_info(message):
    username = message.text
    user = get_user_by_username(username)
    if user:
        bot.send_message(message.chat.id, f"Username: {user[1]}, First Name: {user[3]}, Last Name: {user[4]}")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден.")
bot.infinity_polling()