from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    zabbix_api_url: str = "http://localhost/zabbix/api_jsonrpc.php"
    zabbix_token: str = "random321"
    redis_host: str = "localhost"
    redis_port: int = 6379

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()