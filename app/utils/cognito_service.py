import boto3
import hmac, hashlib, base64
import requests
from jose import jwt, jwk
from jose.utils import base64url_decode
from typing import Dict, List
from ..settings import Settings

client = boto3.client('cognito-idp')
settings = Settings()

JWK = Dict[str, str]
JWKS = Dict[str, List[JWK]]


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


def get_temporary_credentials(token: str):
    identity_client = boto3.client('cognito-identity')
    id_response = identity_client.get_id(AccountId='607722627414',
                                         IdentityPoolId='us-east-1:0e14e653-e277-4b64-af0a-378b14a224b5',
                                         Logins={
                                             'cognito-idp.us-east-1.amazonaws.com/us-east-1_hDWxAIxMH': token
                                         })
    identity_id = id_response['IdentityId']
    credentials = identity_client.get_credentials_for_identity(IdentityId=identity_id, Logins={
                                             'cognito-idp.us-east-1.amazonaws.com/us-east-1_hDWxAIxMH': token
                                         })
    verified, user_sub = _verify_jwt(token, _get_jwks())
    return credentials['Credentials'], user_sub


def _get_jwks():
    return requests.get('https://cognito-idp.us-east-1.amazonaws.com/us-east-1_hDWxAIxMH/.well-known/jwks.json').json()


def _get_hmac_key(token: str, jwks: JWKS):
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key


def _verify_jwt(token: str, jwks: JWKS):
    hmac_key = _get_hmac_key(token, jwks)

    if not hmac_key:
        raise ValueError("No pubic key found!")

    hmac_key = jwk.construct(_get_hmac_key(token, jwks))
    claims = jwt.get_unverified_claims(token)

    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    return hmac_key.verify(message.encode(), decoded_signature), claims['sub']


def _generate_secret_hash(username):
    app_client_id = settings.cognito_client_id
    app_client_secret = settings.cognito_client_secret
    message = bytes(username + app_client_id, 'utf-8')
    key = bytes(app_client_secret, 'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
    return secret_hash
