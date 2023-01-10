from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from .utils import aws_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign_in', scheme_name='UserCredentials')


async def aws_identity(token=Depends(oauth2_scheme)):
    try:
        identity = aws_jwt.get_aws_identity(token)
        return identity
    except Exception as exc:
        raise HTTPException(status_code=500, detail=repr(exc)) #TODO: add correct errors

