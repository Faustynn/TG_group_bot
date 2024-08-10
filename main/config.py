import toml

# Load configuration from config.toml
config = toml.load('../toml/config.toml')
token: str = config['telegram']['key']
group_chat_id: int = int(config['telegram']['groupChat'])
main_logging_level: str = config['logging']['mainLevel']
telegram_logging_level: str = config['logging']['telegramLevel']
topics = config['topics']
roles = toml.load('../toml/hight_roles.toml')['roles']
user_lang = {}
user_media = {}

