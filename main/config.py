import toml

# Load configuration from config.toml
config = toml.load('../toml/config.toml')
token = config['telegram']['key']
group_chat_id = config['telegram']['groupChat']
topics = config['topics']
roles = toml.load('../toml/hight_roles.toml')['roles']
user_lang = {}
user_media = {}

