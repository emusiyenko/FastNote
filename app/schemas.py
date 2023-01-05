from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str


class UserSignUpCredentials(UserCredentials):
    email: str


class UserToken(BaseModel):
    access_token: str
    expiration_date: str
