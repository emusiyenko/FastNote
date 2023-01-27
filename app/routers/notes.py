from fastapi import APIRouter, HTTPException, Depends
from ..schemas import Note, StoredNote, NoteUpdate
from ..utils.aws import dynamodb_service, aws_exception
from ..dependencies import aws_identity

router = APIRouter(prefix='/notes', tags=['notes'])


@router.post('/create/', status_code=201)
async def create_note(note: Note, identity=Depends(aws_identity)) -> StoredNote:
    try:
        note_id = dynamodb_service.create_note(identity=identity, title=note.title, text=note.text)
        return StoredNote(title=note.title,
                          text=note.text,
                          note_id=note_id)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('', status_code=200)
async def get_notes(identity=Depends(aws_identity)) -> [StoredNote]:
    try:
        notes = dynamodb_service.get_notes(identity=identity)
        return [StoredNote.parse_obj(note) for note in notes]
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.get('/{note_id}', status_code=200)
async def get_note(note_id: str, identity=Depends(aws_identity)) -> StoredNote:
    try:
        note = dynamodb_service.get_note(identity=identity, note_id=note_id)
        return StoredNote.parse_obj(note)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.put('/{note_id}', status_code=200)
async def update_note(note_id: str, note: Note, identity=Depends(aws_identity)) -> StoredNote:
    try:
        dynamodb_service.update_note(identity=identity, note_id=note_id, title=note.title, text=note.text)
        return StoredNote(title=note.title,
                          text=note.text,
                          note_id=note_id)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.patch('/{note_id}', status_code=200)
async def partial_update_note(note_id: str, note: NoteUpdate, identity=Depends(aws_identity)) -> StoredNote:
    try:
        dynamodb_service.update_note(identity=identity, note_id=note_id, title=note.title, text=note.text)
        updated_note = dynamodb_service.get_note(identity=identity, note_id=note_id)
        return StoredNote.parse_obj(updated_note)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)


@router.delete('/{note_id}', status_code=204)
async def delete_note(note_id: str, identity=Depends(aws_identity)):
    try:
        dynamodb_service.delete_note(identity=identity, note_id=note_id)
    except aws_exception.AWSServicesException as exc:
        raise HTTPException(status_code=exc.recommended_status_code, detail=exc.detail)
