from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from .utils.aws import aws_jwt, aws_exception

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign_in', scheme_name='UserCredentials')


async def aws_identity(token=Depends(oauth2_scheme)):
    try:
        identity = aws_jwt.get_aws_identity(token)
        return identity
    except aws_exception.AWSServicesException as ex:
        raise HTTPException(status_code=ex.recommended_status_code, detail=ex.detail)

