from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from app.exceptions import AWSServicesException
from app.auth import aws_jwt
from app.settings import Settings
from app.utils.dynamodb_service import NotesDBService
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
