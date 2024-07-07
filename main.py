import telebot
import sqlite3
import os

from cryptography.fernet import Fernet
from telebot import types
from dotenv import load_dotenv
from telebot.handler_backends import State, StatesGroup

# Загрузка переменных окружения
load_dotenv()

# Шифрование токена
key = os.getenv('ENCRYPTION_KEY').encode()
cipher_suite = Fernet(key)
encrypted_token = os.getenv('ENCRYPTED_TOKEN').encode()
token = cipher_suite.decrypt(encrypted_token).decode("utf-8")

# Настройка бота и хранилища состояния
bot = telebot.TeleBot(token)

# Словарь с переводами
translations = {
    'en': {
        'main_menu': 'Main Menu',
        'profile': '👤 Profile',
        'lang': '🏳️ Change language',
        'support': '⚙️ Support',
        'create_post': '✏️ Create post',
        'back': '🔙 Back',
        'start': 'Welcome, how can I help you today?',
        'main_menu_prompt': '👇 Main Menu 👇',
        'type_support': 'Choose the type of support:',
        'use_template': '🔍 Use template',
        'create_new_template': '🖊 Create template',
        'quick_post': '⚡ Quick post',
        'tech_support': 'Technical support',
        'community_support': 'Community support',
        'commercial_offer': 'Commercial offer',
        'choose_option_text': 'Choose an option:',
        'add_title_to_create_template': 'Please add a title to create a template:',
        'add_description_to_create_template': 'Please add a description as well:',
        'add_media_to_create_template': 'Add a photo or video if you want (if not, write "-"):',
        'success_add_template': 'Template created successfully!',
        'example_post_text': 'Example of your post:',
    },
    'ua': {
        'main_menu': 'Головне меню',
        'profile': '👤 Профіль',
        'lang': '🏳️ Змінити мову',
        'support': '⚙️ Підтримка',
        'create_post': '✏️ Створити пост',
        'back': '🔙 Назад',
        'start': 'Вітаємо, чим я можу допомогти вам сьогодні?',
        'main_menu_prompt': '👇 Головне меню 👇',
        'type_support': 'Оберіть тип підтримки:',
        'use_template': '🔍 Використати шаблон',
        'create_new_template': '🖊 Створити шаблон',
        'quick_post': '⚡ Швидкий пост',
        'tech_support': 'Технічна підтримка',
        'community_support': 'Підтримка спільноти',
        'commercial_offer': 'Комерційна пропозиція',
        'choose_option_text': 'Оберіть опцію:',
        'add_title_to_create_template': 'Будь ласка, додайте назву для створення шаблону: ',
        'add_description_to_create_template': 'Додайте також опис:',
        'add_media_to_create_template': 'Додайте фото або відео за бажанням (якщо ні, напишіть "-")',
        'success_add_template': 'Шаблон створено успішно!',
        'example_post_text': 'Приклад вашого шаблону:',
    }
}

# Словарь для хранения выбранного языка и медиа
user_lang = {}
user_media = {}










# Функция для создания таблиц
def setup_database():
    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            login TEXT, 
            chat_id INTEGER UNIQUE, 
            status TEXT, 
            lang TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT NOT NULL,
            description TEXT, 
            media BLOB, 
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

setup_database()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id

    # Проверка наличия пользователя в базе данных
    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()

    if user:
        lang = user[4]  # получаем язык из базы данных
        user_lang[chat_id] = lang
        bot.send_message(chat_id, translations[lang]['start'])
        main_menu(chat_id)
    else:
        ask_language(chat_id)

    cursor.close()
    connection.close()

# Функция запроса выбора языка
def ask_language(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton('English 🇬🇧')
    btn2 = types.KeyboardButton('Українська 🇺🇦')
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "Please choose your language / Виберіть мову будь-ласка", reply_markup=markup)

# Обработчик выбора языка
@bot.message_handler(func=lambda message: message.text in ['English 🇬🇧', 'Українська 🇺🇦'])
def language_selection(message):
    chat_id = message.chat.id
    username = message.from_user.username
    username = '@' + username if username else '-'

    lang = 'en' if message.text == 'English 🇬🇧' else 'ua'
    user_lang[chat_id] = lang

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('UPDATE users SET login = ?, lang = ?, status = ? WHERE chat_id = ?',
                       (username, lang, 'USER', chat_id))
    else:
        cursor.execute('INSERT INTO users (login, chat_id, status, lang) VALUES (?, ?, ?, ?)',
                       (username, chat_id, 'USER', lang))

    connection.commit()
    cursor.close()
    connection.close()
    main_menu(chat_id)

# Главное меню
def main_menu(chat_id):
    lang = user_lang.get(chat_id, 'en')
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton(translations[lang]['create_post'])
    btn2 = types.KeyboardButton(translations[lang]['profile'])
    btn3 = types.KeyboardButton(translations[lang]['lang'])
    btn4 = types.KeyboardButton(translations[lang]['support'])
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, translations[lang]['main_menu_prompt'], reply_markup=markup)

# Обработчик смены языка
@bot.message_handler(func=lambda message: message.text in [translations['en']['lang'], translations['ua']['lang']])
def change_language(message):
    ask_language(message.chat.id)

# Обработчик поддержки
@bot.message_handler(func=lambda message: message.text in [translations['en']['support'], translations['ua']['support']])
def support(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(translations[lang]['tech_support'], url="https://t.me/faustyyn"))
    markup.add(types.InlineKeyboardButton(translations[lang]['community_support'], url="https://t.me/faustyyn"))
    markup.add(types.InlineKeyboardButton(translations[lang]['commercial_offer'], url="https://t.me/faustyyn"))
    bot.send_message(chat_id, translations[lang]['type_support'], reply_markup=markup)

# Обработчик профиля
@bot.message_handler(func=lambda message: message.text in [translations['en']['profile'], translations['ua']['profile']])
def profile(message):
    chat_id = message.chat.id
    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        if user[4] == 'ua':
            user_info = (
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"<b>Інформація про користувача:</b>\n"
                f"<b>Ім'я користувача:</b> <u>{user[1]}</u>\n"
                f"<b>Chat ID:</b> <u>{user[2]}</u>\n"
                f"<b>Статус:</b> {user[3]}\n"
                f"<b>Мова:</b> 🇺🇦\n"
                f"<i>Щоб змінити свій статус, зверніться до технічної підтримки</i>\n"
                f"➖➖➖➖➖➖➖➖➖➖➖"
            )
        else:
            user_info = (
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"<b>User Information:</b>\n"
                f"<b>Username:</b> <u>{user[1]}</u>\n"
                f"<b>Chat ID:</b> <u>{user[2]}</u>\n"
                f"<b>Status:</b> {user[3]}\n"
                f"<b>Language:</b> 🇬🇧\n"
                f"<i>Please contact technical support to change your status</i>\n"
                f"➖➖➖➖➖➖➖➖➖➖➖"
            )
    else:
        user_info = (
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"<b>User not found, please write to technical support! Error code: 404</b>\n"
            f"➖➖➖➖➖➖➖➖➖➖➖"
        )

    bot.send_message(chat_id, user_info, parse_mode='HTML')

# Обработчик создания поста
@bot.message_handler(func=lambda message: message.text in [translations['en']['create_post'], translations['ua']['create_post']])
def create_post(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn0 = types.KeyboardButton(translations[lang]['back'])
    btn1 = types.KeyboardButton(translations[lang]['use_template'])
    btn2 = types.KeyboardButton(translations[lang]['create_new_template'])
    btn3 = types.KeyboardButton(translations[lang]['quick_post'])
    markup.add(btn0, btn1, btn2, btn3)
    bot.send_message(chat_id, translations[lang]['choose_option_text'], reply_markup=markup)

# Обработчик возврата в главное меню
@bot.message_handler(func=lambda message: message.text in [translations['en']['back'], translations['ua']['back']])
def back(message):
    main_menu(message.chat.id)




# Класс состояний для создания поста
class CreatePostState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_media = State()
    showing_example = State()

# Функция для получения ID пользователя
def get_user_id(chat_id):
    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        raise ValueError(f"No user found with chat_id {chat_id}")

# Обработчик создания нового шаблона
@bot.message_handler(func=lambda message: message.text in [translations['en']['create_new_template'],translations['ua']['create_new_template']])
def handle_create_new_template(message: types.Message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    bot.send_message(chat_id, translations[lang]['add_title_to_create_template'])
    CreatePostState.waiting_for_title.set()

# Получение заголовка шаблона
@bot.message_handler(state=CreatePostState.waiting_for_title)
def get_title(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    user_id = get_user_id(chat_id)
    title = message.text

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO posts (title, user_id) VALUES (?, ?)', (title, user_id))
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(chat_id, translations[lang]['add_description_to_create_template'])
    CreatePostState.waiting_for_description.set()

# Получение описания шаблона
@bot.message_handler(state=CreatePostState.waiting_for_description)
def get_description(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    user_id = get_user_id(chat_id)
    description = message.text

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('UPDATE posts SET description = ? WHERE id = (SELECT MAX(id) FROM posts WHERE user_id = ?)',
                   (description, user_id))
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(chat_id, translations[lang]['add_media_to_create_template'])
    CreatePostState.waiting_for_media.set()

# Обработка медиа-файлов
@bot.message_handler(state=CreatePostState.waiting_for_media, content_types=['photo', 'video'])
def add_media_files(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    user_id = get_user_id(chat_id)

    media_file_id = message.photo[-1].file_id if message.photo else message.video.file_id

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()

    cursor.execute('UPDATE posts SET media = ? WHERE id = (SELECT MAX(id) FROM posts WHERE user_id = ?)',
                   (media_file_id, user_id))
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(chat_id, translations[lang]['example_post_text'])
    CreatePostState.showing_example.set()

@bot.message_handler(state=CreatePostState.waiting_for_media, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    if message.text == '-':
        connection = sqlite3.connect('database.sql')
        cursor = connection.cursor()
        cursor.execute('UPDATE posts SET media = ? WHERE id = (SELECT MAX(id) FROM posts WHERE user_id = ?)',
                       (None, get_user_id(chat_id)))
        connection.commit()
        cursor.close()
        connection.close()

        bot.send_message(chat_id, translations[lang]['example_post_text'])
        CreatePostState.showing_example.set()
    else:
        bot.send_message(chat_id, 'Please send a photo, video, or type "-" to skip.')

# Показ примера поста
@bot.message_handler(state=CreatePostState.showing_example)
def example_post(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    user_id = get_user_id(chat_id)

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM posts WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    post = cursor.fetchone()
    connection.close()

    if post:
        media_info = f"Media: {post[3]}" if post[3] else "No media attached"
        bot.send_message(chat_id, f"Title: {post[1]}\nDescription: {post[2]}\n{media_info}")
    else:
        bot.send_message(chat_id, 'Post not found')

    bot.delete_state(chat_id)
    bot.send_message(chat_id, translations[lang]['success_add_template'])
    main_menu(chat_id)

















bot.polling(none_stop=True)
