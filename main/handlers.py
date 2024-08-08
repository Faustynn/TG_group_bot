import sqlite3
import datetime
import logging
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import take_info, ask_language, main_menu, escape_markdown, save_photo, save_video, bot, translations, get_user_id
from decorators import admin_private_required
from config import config, group_chat_id, roles, user_lang, user_media, topics

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    if message.chat.type != 'private':
        message_id = message.message_id
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, translations[lang]['commands_only_group'], message_thread_id=topic_id)
        return

    connection = sqlite3.connect(config['database']['path'])
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()

    if user:
        lang = user[4]
        user_lang[chat_id] = lang
        bot.send_message(chat_id, translations[lang]['start'])
        main_menu(chat_id)
    else:
        ask_language(chat_id)

    cursor.close()
    connection.close()


# Handler to get the chat ID
@bot.message_handler(commands=['getchat_id'])
@admin_private_required
def get_chat_id(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)
    try:
        connection = sqlite3.connect('../db/database.sql')
        cursor = connection.cursor()

        cursor.execute('SELECT status FROM users WHERE login = ?', ("@" + login,))
        role_row = cursor.fetchone()
        cursor.execute('SELECT chat_id FROM users WHERE login = ?', ("@" + login,))
        private_chat_id_row = cursor.fetchone()
        connection.close()

        if role_row:
            if private_chat_id_row:
                private_chat_id = private_chat_id_row[0]
                bot.send_message(private_chat_id, f"ID chat: \"{chat_id}\"\n ID topic: \"{topic_id}\"")
                bot.send_message(chat_id, translations[lang]['chat_id_sent'], message_thread_id=topic_id)
            else:
                pass
                #logging Error: User not found!
        else:
            pass
             #logging Error: User not found in the database!

        bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, translations[lang]['err'], message_thread_id=topic_id)


# Handler to update roles
@bot.message_handler(commands=['update_roles'])
@admin_private_required
def update_roles(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)
    try:
        connection = sqlite3.connect('../db/database.sql')
        cursor = connection.cursor()

        def update_user_roles(role_list, role_name):
            for user in role_list:
                cursor.execute("UPDATE users SET status = ? WHERE login = ?", (role_name, '@' + user))
        update_user_roles(roles['admins'], 'ADMIN')
        update_user_roles(roles['moderators'], 'MODERATOR')
        update_user_roles(roles['volunteers'], 'VOLUNTEER')

        cursor.execute("UPDATE users SET status = 'USER' WHERE login NOT IN ({})".format(','.join(['?' for _ in roles['admins'] + roles['moderators'] + roles['volunteers']])),['@' + user for user in roles['admins'] + roles['moderators'] + roles['volunteers']])

        connection.commit()
        cursor.close()
        connection.close()
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, translations[lang]['role_update_success'], message_thread_id=topic_id)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, translations[lang]['err'], message_thread_id=topic_id)

# Handler to ban a user
@bot.message_handler(commands=['ban'])
@admin_private_required
def ban_user(message):
    chat_id, topic_id, login_admin, message_id, lang = take_info(message)

    if not message.reply_to_message:
        bot.send_message(chat_id, "Please reply to the user's message you want to ban!", message_thread_id=topic_id)
        return

    command_parts = message.text.split(maxsplit=2)
    if len(command_parts) < 3 or not command_parts[1].startswith('@'):
        bot.send_message(chat_id, "Please specify the user and description for the ban!", message_thread_id=topic_id)
        return

    login_user = command_parts[1][1:]
    description = command_parts[2]

    # Get user info
    user_info = bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)

    if not user_info:
        bot.send_message(chat_id, f"User {login_user} not found in this chat.", message_thread_id=topic_id)
        return

    user_id = user_info.user.id

    # Check if the user is the chat owner, admin, or moderator
    if user_info.status in ['creator', 'administrator']:
        bot.send_message(chat_id, "You cannot ban the chat owner or an admin.", message_thread_id=topic_id)
        return

    # Ban the user
    bot.ban_chat_member(chat_id, user_id)
    bot.send_message(chat_id, f"User {login_user} has been banned successfully for: {description}",message_thread_id=topic_id)
    bot.delete_message(chat_id, message_id)

    # Log the ban
    with open('../logs/ban_log.txt', 'a') as log_file:
        log_file.write(
            f"USER:{login_user} banned BY {login_admin} ON {datetime.datetime.now()} BECAUSE: {description}\n")


# Handler to unban a user
@bot.message_handler(commands=['unban'])
@admin_private_required
def unban_user(message):
    chat_id, topic_id, login_admin, message_id, lang = take_info(message)

    if not message.reply_to_message:
        bot.send_message(chat_id, "Please reply to the user's message you want to unban!", message_thread_id=topic_id)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2 or not command_parts[1].startswith('@'):
        bot.send_message(chat_id, "Please specify the user to unban!", message_thread_id=topic_id)
        return

    login_user = command_parts[1][1:]

    # Get user info
    user_info = bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)

    if not user_info:
        bot.send_message(chat_id, f"User {login_user} not found in this chat.", message_thread_id=topic_id)
        return

    user_id = user_info.user.id

    # Unban the user
    bot.unban_chat_member(chat_id, user_id)
    bot.send_message(chat_id, f"User {login_user} has been unbanned successfully.", message_thread_id=topic_id)
    bot.delete_message(chat_id, message_id)

    # Log the unban
    with open('logs/unban_log.txt', 'a') as log_file:
        log_file.write(f"USER:{login_user} unbanned BY {login_admin} ON {datetime.datetime.now()}\n")


# Handler to warn a user
@bot.message_handler(commands=['warn'])
@admin_private_required
def warn_user(message):
    chat_id, topic_id, login_admin, message_id, lang = take_info(message)

    if not message.reply_to_message:
        bot.send_message(chat_id, "Please reply to the user's message you want to warn!", message_thread_id=topic_id)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2 or not command_parts[1].startswith('@'):
        bot.send_message(chat_id, "Please specify the user to warn!", message_thread_id=topic_id)
        return

    login_user = command_parts[1][1:]

    # Get user info
    user_info = bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)

    if not user_info:
        bot.send_message(chat_id, f"User {login_user} not found in this chat.", message_thread_id=topic_id)
        return

    user_id = user_info.user.id

    # Check if the user is the chat owner, admin, or moderator
    if user_info.status in ['creator', 'administrator']:
        bot.send_message(chat_id, "You cannot warn the chat owner or an admin.", message_thread_id=topic_id)
        return

    # Increment the user's warning count
    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT warns FROM users WHERE chat_id = ?', (user_id,))
    warns = cursor.fetchone()[0]
    if warns == 0:
        warns = 1
    else:
        warns += 1
    cursor.execute('UPDATE users SET warns = ? WHERE chat_id = ?', (warns, user_id))
    connection.commit()

    if warns >= 3:
        # Ban the user
        bot.ban_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"User {login_user} has been banned for receiving 3 warnings.",
                         message_thread_id=topic_id)
        cursor.execute('UPDATE users SET warns = 0 WHERE chat_id = ?', (user_id,))
        connection.commit()
    else:
        bot.send_message(chat_id, f"User {login_user} has been warned. Total warnings: {warns}",
                         message_thread_id=topic_id)

    cursor.close()
    connection.close()
    bot.delete_message(chat_id, message_id)

    # Log the warning
    with open('../logs/warn_log.txt', 'a') as log_file:
        log_file.write(
            f"USER:{login_user} warned BY {login_admin} ON {datetime.datetime.now()}. Total warnings: {warns}\n")


# Handler to unwarn a user
@bot.message_handler(commands=['unwarn'])
@admin_private_required
def unwarn_user(message):
    chat_id, topic_id, login_admin, message_id, lang = take_info(message)

    if not message.reply_to_message:
        bot.send_message(chat_id, "Please reply to the user's message you want to unwarn!", message_thread_id=topic_id)
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2 or not command_parts[1].startswith('@'):
        bot.send_message(chat_id, "Please specify the user to unwarn!", message_thread_id=topic_id)
        return

    login_user = command_parts[1][1:]

    # Get user info
    user_info = bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)

    if not user_info:
        bot.send_message(chat_id, f"User {login_user} not found in this chat.", message_thread_id=topic_id)
        return

    user_id = user_info.user.id

    # Decrement the user's warning count
    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT warns FROM users WHERE chat_id = ?', (user_id,))
    warns = cursor.fetchone()[0] - 1
    warns = max(warns, 0)  # Ensure warns do not go below 0
    cursor.execute('UPDATE users SET warns = ? WHERE chat_id = ?', (warns, user_id))
    connection.commit()

    bot.send_message(chat_id, f"User {login_user} has been unwarned. Total warnings: {warns}",
                     message_thread_id=topic_id)

    cursor.close()
    connection.close()
    bot.delete_message(chat_id, message_id)

    # Log the unwarn
    with open('../logs/unwarn_log.txt', 'a') as log_file:
        log_file.write(
            f"USER:{login_user} unwarned BY {login_admin} ON {datetime.datetime.now()}. Total warnings: {warns}\n")


# Handler for the /department_fiit command
@bot.message_handler(commands=['department_fiit'])
def study_dep(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Study Department",
                                  url="https://www.fiit.stuba.sk/study-department.html?page_id=4889")
    markup.add(button)

    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, translations[lang]['department_link'], reply_markup=markup, message_thread_id=topic_id)


# Handler for the /fiit_map command
@bot.message_handler(commands=['fiit_map'])
def fiit_map(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="See Online", url="http://stavba.fiit.stuba.sk/mapa/")
    button2 = InlineKeyboardButton(text="Download Map", callback_data='download_map')
    markup.add(button1, button2)

    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, translations[lang]['fiit_map'], reply_markup=markup, message_thread_id=topic_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'download_map')
    def send_map_archive_to_private_mess(call):
        path = '../photos/static/mapa_FIIT.zip'
        with open(path, 'rb') as file:
            bot.send_document(call.message.chat.id, file)


# Handler for the /exam_schedule command
@bot.message_handler(commands=['exam_schedule'])
def exam_schedule(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Exam Schedule", url="https://www.fiit.stuba.sk/rozvrhy.html?page_id=1697")
    markup.add(button)

    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, translations[lang]['exam_schedule'], reply_markup=markup,
                     message_thread_id=topic_id)


# Handler for the /discord_off command
@bot.message_handler(commands=['discord_off'])
def discord_official_print(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Discord", url="https://discord.gg/dX48acpNS8")
    markup.add(button)

    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id,translations[lang]['disc_off'] , reply_markup=markup, message_thread_id=topic_id)


# Handler for the /discord_tw command
@bot.message_handler(commands=['discord_tw'])
def discord_1_print(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Discord", url="https://discord.gg/m7cRUMPM35")
    markup.add(button)

    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id,chat_id,translations[lang]['disc_prv'] , reply_markup=markup, message_thread_id=topic_id)


# Handler for the /discord_fiit command
@bot.message_handler(commands=['support'])
def support_print(message):
    support(message)


# Handler for the /discord_fiit command
@bot.message_handler(commands=['mladost_map'])
def mladost_map(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    bot.delete_message(chat_id, message_id)
    bot.send_photo(chat_id, open('../photos/static/mapa_mladost.jpg', 'rb'), message_thread_id=topic_id)



# Handler for language selection
@bot.message_handler(func=lambda message: message.text in ['English 🇬🇧', 'Українська 🇺🇦'])
def language_selection(message):
    chat_id = message.chat.id
    username = message.from_user.username
    username = '@' + username if username else '-'

    lang = 'en' if message.text == 'English 🇬🇧' else 'ua'
    user_lang[chat_id] = lang

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('UPDATE users SET login = ?, lang = ?, status = status WHERE chat_id = ?',
                       (username, lang, chat_id))
    else:
        cursor.execute('INSERT INTO users (login, chat_id, status, lang) VALUES (?, ?, ?, ?)',
                       (username, chat_id, 'USER', lang))

    connection.commit()
    cursor.close()
    connection.close()
    main_menu(chat_id)


# Handler for changing the language
@bot.message_handler(func=lambda message: message.text in [translations['en']['lang'], translations['ua']['lang']])
def change_language(message):
    ask_language(message.chat.id)


# Handler for support
@bot.message_handler(
    func=lambda message: message.text in [translations['en']['support'], translations['ua']['support']])
def support(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(translations[lang]['tech_support'], url="https://t.me/faustyyn"))
    markup.add(types.InlineKeyboardButton(translations[lang]['community_support'], url="https://t.me/faustyyn"))
    markup.add(types.InlineKeyboardButton(translations[lang]['commercial_offer'], url="https://t.me/faustyyn"))
    bot.send_message(chat_id, translations[lang]['type_support'], reply_markup=markup, message_thread_id=topic_id)


# Handler for profile
@bot.message_handler(
    func=lambda message: message.text in [translations['en']['profile'], translations['ua']['profile']])
def profile(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)
    connection = sqlite3.connect('../db/database.sql')
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
                f"<b>Попередження: {user[5]}</b>\n"
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
                f"<b>Warns: {user[5]}</b>\n"
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


# Global variable to track quick post state
quick = False


# Handler for creating a post
@bot.message_handler(func=lambda message: message.text in [translations['en']['create_post'], translations['ua']['create_post']])
def create_post(message):
    global quick
    quick = False
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn0 = types.KeyboardButton(translations[lang]['back'])
    btn1 = types.KeyboardButton(translations[lang]['use_template'])
    btn2 = types.KeyboardButton(translations[lang]['create_new_template'])
    btn4 = types.KeyboardButton(translations[lang]['edit_post'])
    btn3 = types.KeyboardButton(translations[lang]['quick_post'])
    markup.add(btn0, btn1, btn4, btn2, btn3)
    bot.send_message(chat_id, translations[lang]['choose_option_text'], reply_markup=markup)


# Handler for going back to the main menu
@bot.message_handler(func=lambda message: message.text in [translations['en']['back'], translations['ua']['back']])
def back(message):
    main_menu(message.chat.id)


# Handler for choosing a template
@bot.message_handler(
    func=lambda message: message.text in [translations['en']['use_template'], translations['ua']['use_template']])
def choose_template(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT id, title FROM posts WHERE user_id = (SELECT id FROM users WHERE chat_id = ?)', (chat_id,))
    posts = cursor.fetchall()
    cursor.close()
    connection.close()

    if posts:
        markup = types.InlineKeyboardMarkup()
        for post in posts:
            markup.add(types.InlineKeyboardButton(post[1], callback_data=f"template_{post[0]}"))
        bot.send_message(chat_id, 'Please choose a template:', reply_markup=markup)
    else:
        bot.send_message(chat_id, 'No templates have been created. Try creating a new template.')
        create_post(message)


# Define a callback query handler for templates
@bot.callback_query_handler(func=lambda call: call.data.startswith('template_'))
def show_template(call):
    chat_id = call.message.chat.id
    lang = user_lang.get(chat_id, 'en')  # Get the user's language, default to 'en'

    # Step 1: Display topic selection buttons
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    for topic_name, topic_id in topics.items():
        button = types.KeyboardButton(topic_name)
        markup.add(button)
    bot.send_message(chat_id, translations[lang]['topic'], reply_markup=markup)

    # Step 2: Handle topic selection
    @bot.message_handler(func=lambda message: message.text in topics.keys())
    def handle_topic_selection(message):
        selected_topic = message.text
        topic_id = topics[selected_topic]

        # Step 3: Proceed to show the template
        template_id = call.data.split('_')[1]
        connection = sqlite3.connect('../db/database.sql')
        cursor = connection.cursor()
        cursor.execute('SELECT title, description, media FROM posts WHERE id = ?', (template_id,))
        post = cursor.fetchone()
        cursor.close()
        connection.close()

        if post:
            title, description, media = post
            response = f"*\"{title}\"*\n\n{description}"
            if media:
                # Check if the media is an image
                if media.endswith(('.png', '.jpg', '.jpeg')):
                    bot.send_photo(group_chat_id, open(media, 'rb'), caption=response, parse_mode='MarkdownV2')
                else:
                    bot.send_message(group_chat_id, response, parse_mode='MarkdownV2')
            else:
                bot.send_message(group_chat_id, response, parse_mode='MarkdownV2')


# Handler for quick post creation
@bot.message_handler(func=lambda message: message.text in [translations['en']['quick_post'], translations['ua']['quick_post']])
def quick_post(message):
    global quick
    quick = True
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    bot.send_message(chat_id, translations[lang]['add_title_to_create_template'])
    bot.register_next_step_handler(message, get_title)


# Handler for editing a post
@bot.message_handler(func=lambda message: message.text in [translations['en']['edit_post'], translations['ua']['edit_post']])
def edit_post(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT id, title FROM posts WHERE user_id = (SELECT id FROM users WHERE chat_id = ?)', (chat_id,))
    posts = cursor.fetchall()
    cursor.close()
    connection.close()

    if posts:
        markup = types.InlineKeyboardMarkup()
        for post in posts:
            markup.add(types.InlineKeyboardButton(post[1], callback_data=f"edit_{post[0]}"))
        bot.send_message(chat_id, translations[lang]['choose_edit'], reply_markup=markup)
    else:
        bot.send_message(chat_id, translations[lang]['no_templates'])
        create_post(message)


# Callback handler for editing a template
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_template(call):
    template_id = call.data.split('_')[1]
    chat_id = call.message.chat.id

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT title, description, media FROM posts WHERE id = ?', (template_id,))
    post = cursor.fetchone()
    cursor.close()
    connection.close()

    if post:
        title, description, media = post
        user_data[chat_id] = {'template_id': template_id, 'title': title, 'description': description, 'media': media}
        lang = user_lang.get(chat_id, 'en')

        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        btn0 = types.KeyboardButton(translations[lang]['back'])
        btn1 = types.KeyboardButton(translations[lang]['edit_title'])
        btn2 = types.KeyboardButton(translations[lang]['edit_description'])
        btn3 = types.KeyboardButton(translations[lang]['edit_media'])
        btn4 = types.KeyboardButton(translations[lang]['delete_template'])
        markup.add(btn0, btn1, btn2, btn3, btn4)
        bot.send_message(chat_id, translations[lang]['choose_edit'], reply_markup=markup)
        bot.register_next_step_handler(call.message, edit_template_step)
    else:
        bot.send_message(chat_id, translations[user_lang.get(chat_id, 'en')]['error_template_not_found'])


# Handle template editing steps
def edit_template_step(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    if message.text == translations[lang]['edit_title']:
        bot.send_message(chat_id, translations[lang]['re_title'])
        bot.register_next_step_handler(message, edit_title)
    elif message.text == translations[lang]['edit_description']:
        bot.send_message(chat_id, translations[lang]['re_description'])
        bot.register_next_step_handler(message, edit_description)
    elif message.text == translations[lang]['edit_media']:
        bot.send_message(chat_id, translations[lang]['re_media'])
        bot.register_next_step_handler(message, edit_media)
    elif message.text == translations[lang]['delete_template']:
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        btn_yes = types.KeyboardButton('YES')
        btn_no = types.KeyboardButton('NO')
        markup.add(btn_yes, btn_no)
        bot.send_message(chat_id, translations[lang]['re_delete'], reply_markup=markup)
        bot.register_next_step_handler(message, confirm_delete_template)
    elif message.text == translations[lang]['back']:
        create_post(message)
    else:
        bot.send_message(chat_id, translations[lang]['error_invalid_option'])


# Confirm deletion of a template
def confirm_delete_template(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    if message.text.upper() == 'YES':
        if chat_id in user_data and 'template_id' in user_data[chat_id]:
            template_id = user_data[chat_id]['template_id']
            connection = sqlite3.connect('../db/database.sql')
            cursor = connection.cursor()
            cursor.execute('DELETE FROM posts WHERE id = ?', (template_id,))
            connection.commit()
            cursor.close()
            connection.close()
            bot.send_message(chat_id, translations[lang]['success_delete_template'])
        else:
            bot.send_message(chat_id, translations[lang]['error_no_template_selected'])
    elif message.text.upper() == 'NO':
        bot.send_message(chat_id, translations[lang]['cancel_delete_template'])
    create_post(message)


# Edit the title of a template
def edit_title(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    new_title = message.text

    if chat_id not in user_data or 'template_id' not in user_data[chat_id]:
        bot.send_message(chat_id, translations[lang]['error_no_template_selected'])
        return

    template_id = user_data[chat_id]['template_id']

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('UPDATE posts SET title = ? WHERE id = ?', (new_title, template_id))
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(chat_id, translations[lang]['success_edit_template'])
    create_post(message)


# Edit the description of a template
def edit_description(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    new_description = message.text

    if chat_id not in user_data or 'template_id' not in user_data[chat_id]:
        bot.send_message(chat_id, translations[lang]['error_no_template_selected'])
        return

    template_id = user_data[chat_id]['template_id']

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('UPDATE posts SET description = ? WHERE id = ?', (new_description, template_id))
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(chat_id, translations[lang]['success_edit_template'])
    create_post(message)


# Edit the media of a template
def edit_media(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')
    media = None

    if message.content_type == 'text':
        media = message.text
        user_data[chat_id]['media'] = None if media == "-" else bot.send_message(chat_id, translations[lang]['add_media_to_create_template'])
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id  # Get the photo
        file_info = bot.get_file(file_id)
        media = save_photo(file_info, file_id, lang)
        user_data[chat_id]['media'] = media
    elif message.content_type == 'video':
        file_id = message.video.file_id  # Get the video
        file_info = bot.get_file(file_id)
        media = save_video(file_info, file_id, lang)
        user_data[chat_id]['media'] = media
    else:
        bot.send_message(chat_id, translations[lang]['err_media_type'])

    user_id = get_user_id(chat_id)
    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('UPDATE posts SET media = ? WHERE user_id = ?', (media, user_id))
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(chat_id, translations[lang]['success_edit_template'])
    create_post(message)


# Global variable to store user data
user_data = {}


# Handler for creating a new template
@bot.message_handler(func=lambda message: message.text in [translations['en']['create_new_template'],translations['ua']['create_new_template']])
def handle_create_new_template(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'en')

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT status FROM users WHERE chat_id = ?', (chat_id,))
    role_row = cursor.fetchone()
    role = role_row[0] if role_row else 'USER'
    cursor.execute('SELECT COUNT(*) FROM posts WHERE user_id = (SELECT id FROM users WHERE chat_id = ?)', (chat_id,))
    templates_row = cursor.fetchone()
    number_of_templates = templates_row[0] if templates_row else 0
    connection.close()

    # Check if user has reached the limit of templates they can create based on their role
    if ((number_of_templates < 10 and (role == "VOLUNTEER" or role == "MODERATOR")) or (
            number_of_templates < 6 and role == "MODERATOR") or (number_of_templates < 2 and role == "USER") or (
            role == "ADMIN")):
        bot.send_message(chat_id, translations[lang]['add_title_to_create_template'])
        bot.register_next_step_handler(message, get_title)
    else:
        bot.send_message(chat_id, translations[lang]['template_limit_reached'] % number_of_templates)



# Function to get the title from the user
def get_title(message):
    chat_id = message.chat.id
    title = message.text
    user_data[chat_id] = {'title': title}
    lang = user_lang.get(chat_id, 'en')
    bot.send_message(chat_id, translations[lang]['add_description_to_create_template'])
    bot.register_next_step_handler(message, get_description)


# Function to get the description from the user
def get_description(message):
    chat_id = message.chat.id
    description = message.text
    user_data[chat_id]['description'] = description
    lang = user_lang.get(chat_id, 'en')
    bot.send_message(chat_id, translations[lang]['add_media_to_create_template'])
    bot.register_next_step_handler(message, get_media)


# Function to get the media from the user
def get_media(message):
    chat_id, topic_id, login, message_id, lang = take_info(message)

    if message.content_type == 'text':
        media = message.text
        user_data[chat_id]['media'] = None if media == "-" else bot.send_message(chat_id, translations[lang]['add_media_to_create_template'])
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id  # Get the photo
        file_info = bot.get_file(file_id)
        media = save_photo(file_info, file_id, lang)
        user_data[chat_id]['media'] = media
    elif message.content_type == 'video':
        file_id = message.video.file_id  # Get the video
        file_info = bot.get_file(file_id)
        media = save_video(file_info, file_id, lang)
        user_data[chat_id]['media'] = media
    else:
        bot.send_message(chat_id, translations[lang]['err_media_type'])

    user_id = get_user_id(chat_id)
    title = user_data[chat_id]['title']
    description = user_data[chat_id]['description']
    media = user_data[chat_id]['media']

    if quick == False:
        with sqlite3.connect('../db/database.sql') as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO posts (title, description, media, user_id) VALUES (?, ?, ?, ?)',
                           (title, description, media, user_id))
            connection.commit()

        bot.send_message(chat_id, translations[lang]['success_add_template'])
    else:
        title = escape_markdown(title)
        description = escape_markdown(description)

        response = (f"*\"{title}\"*\n\n"
                    f"{description}")
        if media:
            if media.endswith(('.png', '.jpg', '.jpeg')):
                bot.send_photo(group_chat_id, open(media, 'rb'), caption=response, parse_mode='MarkdownV2')
            elif media.endswith('.mp4'):
                bot.send_video(group_chat_id, open(media, 'rb'), caption=response, parse_mode='MarkdownV2')
            else:
                bot.send_message(group_chat_id, response, parse_mode='MarkdownV2')
        else:
            bot.send_message(group_chat_id, response, parse_mode='MarkdownV2')

    user_data.pop(chat_id)
    create_post(message)