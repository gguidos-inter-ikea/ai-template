"""
Environment Configuration.
"""
from dotenv import load_dotenv

load_dotenv()

def load_config(container):
    # API configurations
    container.config.api_key.from_env("API_KEY")
    container.config.log_level.from_env("LOG_LEVEL")
    container.config.port.from_env("PORT")

    # MongoDB configurations
    container.config.mongodb.db_uri.from_env("MONGODB_URI")
    container.config.mongodb.db_name.from_env("MONGODB_DBNAME")

    # Redis configurations
    container.config.redis.host.from_env("REDIS_HOST", "redis")
    container.config.redis.port.from_env("REDIS_PORT", "6379")
    container.config.redis.db.from_env("REDIS_DB", "0")
    container.config.redis.password.from_env("REDIS_PASSWORD", default=None)
    container.config.redis.url.from_env("REDIS_URL")
    container.config.redis.session_key_prefix.from_env("REDIS_SESSION_KEY_PREFIX")