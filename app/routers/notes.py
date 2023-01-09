from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from ..schemas import Note
from ..utils import dynamodb_service, cognito_service

router = APIRouter(prefix='/notes', tags=['notes'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign_in', scheme_name='UserCredentials')


@router.post('/create/', status_code=201)
async def sign_up(note: Note, token=Depends(oauth2_scheme)):
    try:
        credentials, user_sub = cognito_service.get_temporary_credentials(token)
        dynamodb_service.create_note(user_id='1', title=note.title, text=note.text, credentials=credentials)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=repr(exc))
