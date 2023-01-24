from fastapi import APIRouter, HTTPException, Depends
from ..schemas import Note, StoredNote
from ..utils.aws import dynamodb_service
from ..dependencies import aws_identity

router = APIRouter(prefix='/notes', tags=['notes'])


@router.post('/create/', status_code=201)
async def create_note(note: Note, identity=Depends(aws_identity)) -> StoredNote:
    try:
        note_id = dynamodb_service.create_note(identity=identity, title=note.title, text=note.text)
        return StoredNote(title=note.title,
                          text=note.text,
                          note_id=note_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=repr(exc))
