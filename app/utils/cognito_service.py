import boto3
import hmac, hashlib, base64
from ..settings import Settings

client = boto3.client('cognito-idp')
settings = Settings()


def sign_up(username: str, password: str, email: str):
    client.sign_up(ClientId=settings.cognito_client_id,
                   Username=username,
                   Password=password,
                   SecretHash=_generate_secret_hash(username),
                   UserAttributes=[
                       {
                           'Name': 'email',
                           'Value': email
                       },
                       {
                           'Name': 'name',
                           'Value': username
                       }
                   ]
                   )


def add_user_to_default_group(username: str):
    client.admin_add_user_to_group(UserPoolId=settings.cognito_user_pool_id,
                                   Username=username,
                                   GroupName=settings.cognito_regular_user_group_name)


def confirm_sign_up(username: str, confirmation_code: str):
    client.confirm_sign_up(ClientId=settings.cognito_client_id,
                           Username=username,
                           ConfirmationCode=confirmation_code,
                           SecretHash=_generate_secret_hash(username)
                           )


def initiate_auth(username: str, password: str):
    response = client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
                                    ClientId=settings.cognito_client_id,
                                    AuthParameters={
                                        'USERNAME': username,
                                        'PASSWORD': password,
                                        'SECRET_HASH': _generate_secret_hash(username)
                                    })
    result = response['AuthenticationResult']
    return {
        'access_token': result['IdToken'], #TODO: check
        'token_type': result['TokenType'],
        'refresh_token': result['RefreshToken'],
        'expires_in': result['ExpiresIn']
    }


def _generate_secret_hash(username):
    app_client_id = settings.cognito_client_id
    app_client_secret = settings.cognito_client_secret
    message = bytes(username + app_client_id, 'utf-8')
    key = bytes(app_client_secret, 'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
    return secret_hash
