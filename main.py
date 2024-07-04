import telebot
import sqlite3
from telebot import types
bot = telebot.TeleBot('7144328068:AAGZC51FoyHuand184ew7lRjYf7SZk4y7r0')

# Словник з перекладами
translations = {
    'en': {
        'main_menu': 'Main Menu',
        'profile': 'Profile',
        'lang': '🏳️ Change language',
        'support': '⚙️ Support',
        'create_post': '✏️ Create post',
        'back': '🔙 Back',
        'start': 'Welcome, how can I help you today?',
        'main_menu_prompt': '👇 Main Menu 👇',
        'type_support': 'Choose the type of support:',
        'use_template': 'Use template',
        'create_new_template': 'Create new template',
        'quick_post': 'Quick post',
        'tech_support': 'Technical support',
        'community_support': 'Community support',
        'commercial_offer': 'Commercial offer'
    },
    'ua': {
        'main_menu': 'Головне меню',
        'profile': 'Профіль',
        'lang': '🏳️ Змінити мову',
        'support': '⚙️ Підтримка',
        'create_post': '✏️ Створити пост',
        'back': '🔙 Назад',
        'start': 'Вітаємо, чим я можу допомогти вам сьогодні?',
        'main_menu_prompt': '👇 Головне меню 👇',
        'type_support': 'Оберіть тип підтримки:',
        'use_template': 'Використати шаблон',
        'create_new_template': 'Створити новий шаблон',
        'quick_post': 'Швидкий пост',
        'tech_support': 'Технічна підтримка',
        'community_support': 'Підтримка спільноти',
        'commercial_offer': 'Комерційна пропозиція'
    }
}
# Словник для зберігання вибраної мови для кожного користувача
user_lang = {}


# Обробник команди /start
@bot.message_handler(commands=['start'])
def start_message(message):
    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT, chat_id INTEGER UNIQUE, status TEXT, lang TEXT)""")
    connection.commit()

    chat_id = message.chat.id
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()

    if user:
        lang = user[4]  # отримуємо мову з бази даних
        user_lang[chat_id] = lang
        main_menu(chat_id)
    else:
        ask_language(chat_id)

    cursor.close()
    connection.close()


# Функція запиту вибору мови
def ask_language(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton('English 🇬🇧')
    btn2 = types.KeyboardButton('Українська 🇺🇦')
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "Please choose your language / Виберіть мову будь-ласка", reply_markup=markup)


# Обробник вибору мови
@bot.message_handler(func=lambda message: message.text in ['English 🇬🇧', 'Українська 🇺🇦'])
def language_selection(message):
    chat_id = message.chat.id
    username = message.from_user.username
    username = '@' + username if username else '-'

    if message.text == 'English 🇬🇧':
        lang = 'en'
        user_lang[chat_id] = 'en'
    elif message.text == 'Українська 🇺🇦':
        lang = 'ua'
        user_lang[chat_id] = 'ua'

    connection = sqlite3.connect('database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('UPDATE users SET login = ?, lang = ?, status = ? WHERE chat_id = ?',
                       (username, lang, 'user', chat_id))
    else:
        cursor.execute('INSERT INTO users (login, chat_id, status, lang) VALUES (?, ?, ?, ?)',
                       (username, chat_id, 'user', lang))

    connection.commit()
    cursor.close()
    connection.close()
    main_menu(chat_id)


# Головне меню
def main_menu(chat_id):
    lang = user_lang.get(chat_id, 'en')
    bot.send_message(chat_id, translations[lang]['start'])
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton(translations[lang]['create_post'])
    btn2 = types.KeyboardButton(translations[lang]['profile'])
    btn3 = types.KeyboardButton(translations[lang]['lang'])
    btn4 = types.KeyboardButton(translations[lang]['support'])
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, translations[lang]['main_menu_prompt'], reply_markup=markup)


# Обробник зміни мови
@bot.message_handler(func=lambda message: message.text in ['🏳️ Change language', '🏳️ Змінити мову'])
def change_language(message):
    ask_language(message.chat.id)


# Обробник підтримки
@bot.message_handler(func=lambda message: message.text in ['⚙️ Support', '⚙️ Підтримка'])
def support(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(translations[lang]['tech_support'], url="https://t.me/faustyyn"))
    markup.add(types.InlineKeyboardButton(translations[lang]['community_support'], url="https://t.me/faustyyn"))
    markup.add(types.InlineKeyboardButton(translations[lang]['commercial_offer'], url="https://t.me/faustyyn"))
    bot.send_message(chat_id, translations[lang]['type_support'], reply_markup=markup)


# Обробник створення посту
@bot.message_handler(func=lambda message: message.text in ['✏️ Create post', '✏️ Створити пост'])
def create_post(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn0 = types.KeyboardButton(translations[lang]['back'])
    btn1 = types.KeyboardButton(translations[lang]['use_template'])
    btn2 = types.KeyboardButton(translations[lang]['create_new_template'])
    btn3 = types.KeyboardButton(translations[lang]['quick_post'])
    markup.add(btn0, btn1, btn2, btn3)
    bot.send_message(chat_id, "Choose an option:", reply_markup=markup)


bot.polling(none_stop=True)
