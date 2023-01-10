import requests
import boto3
from typing import Dict, List
from jose import jwt, jwk
from jose.utils import base64url_decode
from ..settings import Settings
from ..schemas import AWSIdentity

JWK = Dict[str, str]
JWKS = Dict[str, List[JWK]]
settings = Settings()


def get_aws_identity(token: str) -> AWSIdentity:
    identity_client = boto3.client('cognito-identity')
    user_pool_full_identifier = f'cognito-idp.{settings.aws_region}.amazonaws.com/{settings.cognito_user_pool_id}'
    id_response = identity_client.get_id(AccountId=settings.aws_account_id,
                                         IdentityPoolId=settings.cognito_identity_pool_id,
                                         Logins={
                                             user_pool_full_identifier: token
                                         })
    identity_id = id_response['IdentityId']
    credentials = identity_client.get_credentials_for_identity(IdentityId=identity_id, Logins={
                                             user_pool_full_identifier: token
                                         })
    verified, claims = _verify_jwt(token, _get_jwks())

    identity_object = AWSIdentity.parse_obj(credentials)
    identity_object.cognito_claims = claims

    return identity_object


def _get_jwks():
    jwks_url = f'https://cognito-idp.{settings.aws_region}.amazonaws.com' \
               f'/{settings.cognito_user_pool_id}/.well-known/jwks.json'
    return requests.get(jwks_url).json()


def _get_hmac_key(token: str, jwks: JWKS):
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key


def _verify_jwt(token: str, jwks: JWKS):
    hmac_key = _get_hmac_key(token, jwks)

    if not hmac_key:
        raise ValueError("No pubic key found!")

    hmac_key = jwk.construct(hmac_key)
    claims = jwt.get_unverified_claims(token)

    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())
    verified = hmac_key.verify(message.encode(), decoded_signature)

    return verified, claims
