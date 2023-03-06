from fastapi import APIRouter, HTTPException, Depends
from ..schemas import Note, StoredNote, NoteUpdate
from ..exceptions import AWSServicesException
from ..dependencies import dynamodb_service

router = APIRouter(prefix='/notes', tags=['notes'])


@router.post('/create/', status_code=201)
async def create_note(note: Note, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.create_note(note)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('', status_code=200)
async def get_notes(notes_service=Depends(dynamodb_service)) -> [StoredNote]:
    try:
        return notes_service.get_notes()
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('/{note_id}', status_code=200)
async def get_note(note_id: str, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.get_note(note_id)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.put('/{note_id}', status_code=200)
async def update_note(note_id: str, note: Note, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.update_note(note_id, note.text, note.title)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.patch('/{note_id}', status_code=200)
async def partial_update_note(note_id: str, note: NoteUpdate, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.update_note(note_id, note.text, note.title)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.delete('/{note_id}', status_code=204)
async def delete_note(note_id: str, notes_service=Depends(dynamodb_service)):
    try:
        notes_service.delete_note(note_id)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)
