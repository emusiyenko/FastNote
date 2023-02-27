from fastapi import APIRouter, HTTPException, Depends
from ..schemas import Note, StoredNote, NoteUpdate
from ..utils.aws import aws_exception
from ..utils.aws.dynamodb_service import NotesDBService
from ..dependencies import aws_identity

router = APIRouter(prefix='/notes', tags=['notes'])
notes_service = NotesDBService()


@router.post('/create/', status_code=201)
async def create_note(note: Note, identity=Depends(aws_identity)) -> StoredNote:
    try:
        return notes_service.create_note(identity, note)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('', status_code=200)
async def get_notes(identity=Depends(aws_identity)) -> [StoredNote]:
    try:
        return notes_service.get_notes(identity)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('/{note_id}', status_code=200)
async def get_note(note_id: str, identity=Depends(aws_identity)) -> StoredNote:
    try:
        return notes_service.get_note(identity, note_id)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.put('/{note_id}', status_code=200)
async def update_note(note_id: str, note: Note, identity=Depends(aws_identity)) -> StoredNote:
    try:
        return notes_service.update_note(identity, note_id, note.text, note.title)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.patch('/{note_id}', status_code=200)
async def partial_update_note(note_id: str, note: NoteUpdate, identity=Depends(aws_identity)) -> StoredNote:
    try:
        return notes_service.update_note(identity, note_id, note.text, note.title)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.delete('/{note_id}', status_code=204)
async def delete_note(note_id: str, identity=Depends(aws_identity)):
    try:
        notes_service.delete_note(identity, note_id)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)
