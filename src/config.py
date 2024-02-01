from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UvicornSettings(BaseSettings):
    """
    Настройки сервера
    """

    host: str = Field(default="localhost")
    port: int = Field(default=8000)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8")


server_settings = UvicornSettings()
