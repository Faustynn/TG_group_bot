import sqlite3
import os
import logging
from telebot import TeleBot, types
from config import config, user_lang

logger = logging.getLogger(__name__)

# Initialize the bot with the token from the config
bot = TeleBot(config['telegram']['key'])

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
        'edit_post': '🖊 Edit template',
        'choose_edit': 'Choose what you want to edit:',
        'edit_title': 'Title',
        'edit_description': 'Description',
        'edit_media': 'Media Data',
        're_title': 'Enter a new title for the template:',
        're_description': 'Enter a new description for the template:',
        're_media': 'Add a photo or video if you want (if not, write "-"):',
        'success_edit_template': 'Template edited successfully',
        'delete_template': '🗑️ Delete template',
        're_delete': 'Are you sure you want to delete the template?',
        'success_delete_template': 'Template deleted successfully',
        'commands_only_group': 'Commands are only available in a private chat!',
        'admin_requirement': 'This command can only be used by administrators or moderators!',
        'chat_id_sent': 'Chat ID has been successfully sent to the private chat!',
        'err': 'Unfortunately, a technical error occurred, please try again! Or report this to technical support!',
        'role_update_success': 'Roles have been successfully updated!',
        'department_link': 'Go to the university schedule website:',
        'fiit_map': 'FIIT Map:',
        'exam_schedule': 'Go to the exam schedule website:',
        'disc_off': 'Official STU FIIT Discord:',
        'disc_prv': 'Discord created by freshmen:',
        'topic': 'Please choose a topic:',
        'no_templates': 'No templates have been created. Try creating a new template.',
        'error_no_template_selected': 'Error: Template not found, try again!',
        'cancel_delete_template': 'Template deletion canceled!',
        'err_media_type': 'Unsupported media type. Please upload photo or video.',
        'template_limit_reached': 'You have reached the limit of templates!',
        'invalid_format': 'Invalid format. Please upload a file in PNG or JPEG format',
        'gl_discrd': 'Discord group of this chat:',
        'minecraft_server_info': 'Minecraft server information:',
        'download_mods': 'Click to download mods:',
    },
    'ua': {
        'main_menu': 'Головне меню',
        'profile': '👤 Профіль',
        'lang': '🏳️ Змінити мову',
        'support': '⚙️ Підтримка',
        'create_post': '✏️ Створити пост',
        'back': '🔙 Назад',
        'start': 'Вітаю, чим я можу допомогти вам сьогодні?',
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
        'edit_post': '🖊 Редагувати шаблон:',
        'edit_title': 'Назва',
        'edit_description': 'Опис',
        'edit_media': 'Медіа дані',
        're_title': 'Введіть нову назву шаблону:',
        're_description': 'Введіть новий опис шаблону:',
        're_media': 'Додайте фото або відео за бажанням (якщо ні, напишіть "-"):',
        'success_edit_template': 'Шаблон успішно відредаговано!',
        'delete_template': '🗑️ Видалити шаблон',
        're_delete': 'Ви впевнені, що хочете видалити шаблон?',
        'success_delete_template': 'Шаблон успішно видалено!',
        'commands_only_group': 'Команди доступні тільки в особистому чаті!',
        'admin_requirement': 'Цю команду можуть використовувати тільки адміністратори або модератори!',
        'chat_id_sent': 'Айді чата було успішно відправлено в особистий чат!',
        'err': 'На жаль, сталася технічна помилка, спробуйте ще раз! Або повідомте про це технічну підтримку!',
        'role_update_success': 'Ролі були успішно оновлені!',
        'department_link': 'Перейти на сайт з розкладом університету:',
        'fiit_map': 'Карта FIIT:',
        'exam_schedule': 'Перейти на сайт з розкладом екзаменів:',
        'disc_off': 'Офіційний дискорд STU FIIT:',
        'disc_prv': 'Дискорд створений першокурсниками:',
        'topic': 'Будь ласка, виберіть тему:',
        'choose_edit': 'Будь ласка, виберіть шаблон для редагування:',
        'no_templates': 'Шаблони не були створені. Спробуйте створити новий шаблон.',
        'error_no_template_selected': 'Помилка: Шаблон не знайдено, спробуйте ще раз!',
        'cancel_delete_template': 'Видалення шаблону скасовано!',
        'err_media_type': 'Непідтримуваний тип медіа. Будь ласка, завантажте фото або відео.',
        'template_limit_reached': 'Ви досягли ліміту шаблонів!',
        'invalid_format': 'Неможливий формат. Будь ласка, завантажте файл у форматі PNG або JPEG',
        'gl_discrd': 'Діскорд група цього чату:',
        'minecraft_server_info': 'Інформація про сервер Minecraft:',
        'download_mods': 'Натисніть, щоб завантажити моди:',
    }
}


def take_info(message):
    chat_id = message.chat.id
    topic_id = message.message_thread_id if hasattr(message, 'message_thread_id') else None
    login = message.from_user.username
    message_id = message.message_id
    lang = user_lang.get(chat_id, 'en')
    return chat_id, topic_id, login, message_id, lang

# Function to display the main menu
def main_menu(chat_id):
    lang = user_lang.get(chat_id, 'en')
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)

    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT status FROM users WHERE chat_id = ?', (chat_id,))
        role_row = cursor.fetchone()
        if not role_row:
            logger.info(f"Role not found in database with chat_id {chat_id}")
            bot.send_message(chat_id, "Error- Role not found!Please contact technical support!")
            return
        role = role_row[0]

        if role in ["ADMIN", "MODERATOR"]:
            btn1 = types.KeyboardButton(translations[lang]['create_post'])
            btn2 = types.KeyboardButton(translations[lang]['profile'])
            btn3 = types.KeyboardButton(translations[lang]['lang'])
            btn4 = types.KeyboardButton(translations[lang]['support'])
            markup.add(btn1, btn2, btn3, btn4)
        else:
            btn2 = types.KeyboardButton(translations[lang]['profile'])
            btn3 = types.KeyboardButton(translations[lang]['lang'])
            btn4 = types.KeyboardButton(translations[lang]['support'])
            markup.add(btn2, btn3, btn4)
        bot.send_message(chat_id, translations[lang]['main_menu_prompt'], reply_markup=markup)

    except sqlite3.Error as e:
        bot.send_message(chat_id, f"Database error: {e}")
    finally:
        connection.close()

# Function to ask the user to choose a language
def ask_language(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton('English 🇬🇧')
    btn2 = types.KeyboardButton('Українська 🇺🇦')
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "Please choose your language / Виберіть мову будь-ласка", reply_markup=markup)

# Function to escape special characters for Markdown
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

# Function to save photo
def save_photo(file_info, file_id, lang):
    valid_extensions = ['.png', '.jpg', '.jpeg']
    _, file_extension = os.path.splitext(file_info.file_path)

    if file_extension.lower() not in valid_extensions:
        return translations[lang]['invalid_format']

    # Create folder if it doesn't exist
    if not os.path.exists('../photos'):
        os.makedirs('../photos')

    file_path = os.path.join('../photos', f'{file_id}{file_extension}')
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    return file_path


# Function to save video
def save_video(file_info, file_id, lang):
    valid_extensions = ['.mp4']
    _, file_extension = os.path.splitext(file_info.file_path)

    if file_extension.lower() not in valid_extensions:
        return translations[lang]['invalid_format']

    # Create folder if it doesn't exist
    if not os.path.exists('../videos'):
        os.makedirs('../videos')

    file_path = os.path.join('../videos', f'{file_id}{file_extension}')
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    return file_path

# Function to get user ID from the chat ID
def get_user_id(chat_id):
    connection = sqlite3.connect('../db/database.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        logger.info(f"No user found with chat_id {chat_id}")
