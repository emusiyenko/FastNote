from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from .exceptions import AWSServicesException
from .auth import aws_jwt
from .settings import Settings
from .utils.dynamodb_service import NotesDBService
settings = Settings()

root_path = settings.api_root_path if settings.api_root_path else ''

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=root_path + '/auth/sign_in', scheme_name='UserCredentials')


async def aws_identity(token=Depends(oauth2_scheme)):
    try:
        identity = aws_jwt.get_aws_identity(token)
        return identity
    except AWSServicesException as ex:
        raise HTTPException(status_code=ex.recommended_status_code, detail=ex.detail)


async def dynamodb_service(identity=Depends(aws_identity)):
    return NotesDBService(identity)
