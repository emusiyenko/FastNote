from pydantic import BaseSettings


class Settings(BaseSettings):
    cognito_client_id: str
    cognito_client_secret: str
    cognito_user_pool_id: str
    cognito_regular_user_group_name: str
