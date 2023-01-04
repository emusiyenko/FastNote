from pydantic import BaseSettings


class Settings(BaseSettings):
    cognito_client_id: str
    cognito_client_secret: str
