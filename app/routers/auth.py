from fastapi import APIRouter, HTTPException
from ..utils import cognito_service
from ..schemas import UserCredentials, UserSignUpCredentials, UserToken

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/sign_up', status_code=201)
async def sign_up(user: UserSignUpCredentials):
    try:
        cognito_service.sign_up(user.username, user.password, user.email)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=repr(exc))


@router.post('/confirm_sign_up')
async def confirm_sign_up(username: str, confirmation_code: str):
    try:
        cognito_service.confirm_sign_up(username, confirmation_code)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=repr(exc))


@router.post('/sign_in')
async def sign_in(user: UserCredentials):
    try:
        auth_result = cognito_service.initiate_auth(user.username, user.password)
        return auth_result
    except Exception as exc:
        raise HTTPException(status_code=401, detail=repr(exc))
