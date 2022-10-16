from pydantic import BaseSettings, SecretStr
from pathlib import Path


class Settings(BaseSettings):
    db: SecretStr

    host: str
    port: int
    web_secret: SecretStr

    user_microservice_url: str
    user_microservice_token: SecretStr

    tasks_microservice_url: str
    tasks_microservice_token: SecretStr

    cars_microservice_url: str
    cars_microservice_token: SecretStr

    class Config:
        env_file = Path(__file__).parent.joinpath('.env')
        env_file_encoding = 'utf-8'


config = Settings()
