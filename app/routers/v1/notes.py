from fastapi import APIRouter, HTTPException, Depends
from app.schemas import Note, StoredNote, NoteUpdate
from app.exceptions import AWSServicesException
from app.dependencies import dynamodb_service
from fastapi import status

router = APIRouter(prefix='/v1/notes', tags=['notes'])


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_note(note: Note, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.create_note(note)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('', status_code=status.HTTP_200_OK)
async def get_notes(notes_service=Depends(dynamodb_service)) -> [StoredNote]:
    try:
        return notes_service.get_notes()
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('/{note_id}', status_code=status.HTTP_200_OK)
async def get_note(note_id: str, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.get_note(note_id)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.put('/{note_id}', status_code=status.HTTP_200_OK)
async def update_note(note_id: str, note: Note, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.update_note(note_id, note.title, note.text)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.patch('/{note_id}', status_code=status.HTTP_200_OK)
async def partial_update_note(note_id: str, note: NoteUpdate, notes_service=Depends(dynamodb_service)) -> StoredNote:
    try:
        return notes_service.update_note(note_id, note.title, note.text)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, notes_service=Depends(dynamodb_service)):
    try:
        notes_service.delete_note(note_id)
    except AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)
