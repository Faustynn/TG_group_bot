from functools import wraps
import sqlite3
from utils import take_info, translations, bot
from config import config
import logging

logger = logging.getLogger(__name__)


def admin_private_required(f):
    @wraps(f)
    def decorated_function(message, *args, **kwargs):
        chat_id, topic_id, login, message_id, lang = take_info(message)

        if message.chat.type == 'private':
            bot.send_message(chat_id, translations[lang]['commands_only_group'])
            return

        user_id = message.from_user.id
        login = f"@{message.from_user.username}"

        with sqlite3.connect(config['database']['path']) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT status FROM users WHERE login = ?', (login,))
            role_row = cursor.fetchone()
            logger.info(f"Fetched role for user {login}: {role_row}")

        if not role_row or role_row[0] not in ["ADMIN", "MODERATOR"]:
            bot.send_message(chat_id, translations[lang]['admin_requirement'], message_thread_id=topic_id)
            logger.info(f"User {login} does not have admin or moderator role in db.")
            return

        chat_admins = bot.get_chat_administrators(chat_id)
        if user_id not in [admin.user.id for admin in chat_admins]:
            bot.send_message(chat_id, translations[lang]['admin_requirement'], message_thread_id=topic_id)
            logger.info(f"User {login} does not have admin or moderator role in chat.")
            return

        return f(message, *args, **kwargs)

    return decorated_function