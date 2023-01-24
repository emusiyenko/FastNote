from fastapi import APIRouter, HTTPException, Depends
from ..utils.aws import cognito_service, aws_exception
from ..schemas import UserSignUpCredentials
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/sign_up', status_code=201)
async def sign_up(user: UserSignUpCredentials):
    try:
        cognito_service.sign_up(user.username, user.password, user.email)
        cognito_service.add_user_to_default_group(user.username)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.post('/confirm_sign_up')
async def confirm_sign_up(username: str, confirmation_code: str):
    try:
        cognito_service.confirm_sign_up(username, confirmation_code)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.post('/sign_in')
async def sign_in(user: OAuth2PasswordRequestForm = Depends()):
    try:
        auth_result = cognito_service.initiate_auth(user.username, user.password)
        return auth_result
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)