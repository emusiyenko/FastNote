from pydantic import BaseSettings


class Settings(BaseSettings):
    cognito_client_id: str
    cognito_client_secret: str
    cognito_user_pool_id: str
    cognito_regular_user_group_name: str
    cognito_identity_pool_id: str
    aws_region: str
    aws_account_id: str
    dynamo_db_notes_table: str
    api_root_path: str = None
