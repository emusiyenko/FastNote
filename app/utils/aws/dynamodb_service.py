import uuid
from app.schemas import AWSIdentity
from .aws_exception import AWSServicesException
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from ...settings import Settings
from ...schemas import Note, StoredNote

settings = Settings()


class DynamoDBNote(Model):
    user_id = UnicodeAttribute(hash_key=True)
    contents = UnicodeAttribute(range_key=True)
    title = UnicodeAttribute()
    text = UnicodeAttribute()

    class Meta:
        table_name = settings.dynamo_db_notes_table
        region = settings.aws_region


class NotesDBService:

    @staticmethod
    def create_note(identity: AWSIdentity, note: Note):
        note_id = f'{uuid.uuid4().hex}'
        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents=NotesDBService._get_range_key_from_note_id(note_id),
                                     title=note.title, text=note.text)
        dynamodb_note.save()
        return NotesDBService._get_stored_note_from_dynamodb_note(dynamodb_note)

    @staticmethod
    def get_notes(identity: AWSIdentity):
        notes = DynamoDBNote.query(hash_key=identity.identity_id,
                                   range_key_condition=DynamoDBNote.contents.startswith('note_'))
        return [NotesDBService._get_stored_note_from_dynamodb_note(note) for note in notes]

    @staticmethod
    def get_note(identity: AWSIdentity, note_id: str):
        note = NotesDBService._get_dynamodb_note(identity, note_id)
        return NotesDBService._get_stored_note_from_dynamodb_note(note)

    @staticmethod
    def delete_note(identity: AWSIdentity, note_id: str):
        note = NotesDBService._get_dynamodb_note(identity, note_id)
        note.delete()

    @staticmethod
    def update_note(identity: AWSIdentity, note_id: str, title: str = None, text: str = None):
        note = NotesDBService._get_dynamodb_note(identity, note_id)
        if title:
            note.title = title
        if text:
            note.text = text
        note.save()
        return NotesDBService._get_stored_note_from_dynamodb_note(note)

    @staticmethod
    def _get_dynamodb_note(identity: AWSIdentity, note_id: str):
        note = DynamoDBNote.get(hash_key=identity.identity_id, range_key=f'note_{note_id}')
        if not note:
            raise AWSServicesException(recommended_status_code=404, detail=f'Note with id {note_id} not found')
        return note

    @staticmethod
    def _get_stored_note_from_dynamodb_note(note):
        return StoredNote(title=note.title, text=note.text,
                          note_id=NotesDBService._get_stored_note_id_from_range_key(note.contents))

    @staticmethod
    def _get_stored_note_id_from_range_key(range_key):
        return range_key[len(NotesDBService._get_note_id_prefix()):]

    @staticmethod
    def _get_range_key_from_note_id(note_id):
        return f'note_{note_id}'

    @staticmethod
    def _get_note_id_prefix():
        return 'note_'
