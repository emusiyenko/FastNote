import datetime

from pydantic import BaseModel, Field


class UserCredentials(BaseModel):
    username: str
    password: str


class UserSignUpCredentials(UserCredentials):
    email: str


class UserToken(BaseModel):
    access_token: str
    expiration_date: str


class Note(BaseModel):
    title: str
    text: str


class AWSIdentityCredentials(BaseModel):
    access_key_id: str = Field(alias='AccessKeyId')
    secret_key: str = Field(alias='SecretKey')
    session_token: str = Field(alias='SessionToken')
    expiration: datetime.datetime = Field(alias='Expiration')


class AWSIdentity(BaseModel):
    identity_id: str = Field(alias='IdentityId')
    cognito_claims: dict = {}
    credentials: AWSIdentityCredentials = Field(alias='Credentials')
