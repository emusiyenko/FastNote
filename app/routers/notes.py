from fastapi import APIRouter, HTTPException, Depends
from ..schemas import Note
from ..utils import dynamodb_service
from ..dependencies import aws_identity

router = APIRouter(prefix='/notes', tags=['notes'])


@router.post('/create/', status_code=201)
async def sign_up(note: Note, identity=Depends(aws_identity)):
    try:
        dynamodb_service.create_note(identity=identity, title=note.title, text=note.text)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=repr(exc))
