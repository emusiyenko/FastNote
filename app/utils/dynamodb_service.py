import uuid
from app.schemas import AWSIdentity
from ..exceptions import AWSServicesException
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from app.settings import Settings
from app.schemas import Note, StoredNote

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

    def __init__(self, identity: AWSIdentity):
        self.identity = identity

    def create_note(self, note: Note):
        note_id = f'{uuid.uuid4().hex}'
        dynamodb_note = DynamoDBNote(self.identity.identity_id,
                                     contents=self._get_range_key_from_note_id(note_id),
                                     title=note.title, text=note.text)
        dynamodb_note.save()
        return self._get_stored_note_from_dynamodb_note(dynamodb_note)

    def get_notes(self):
        notes = DynamoDBNote.query(hash_key=self.identity.identity_id,
                                   range_key_condition=DynamoDBNote.contents.startswith('note_'))
        return [self._get_stored_note_from_dynamodb_note(note) for note in notes]

    def get_note(self, note_id: str):
        note = self._get_dynamodb_note(note_id)
        return self._get_stored_note_from_dynamodb_note(note)

    def delete_note(self, note_id: str):
        note = self._get_dynamodb_note(note_id)
        note.delete()

    def update_note(self, note_id: str, title: str = None, text: str = None):
        note = self._get_dynamodb_note(note_id)
        if title:
            note.title = title
        if text:
            note.text = text
        note.save()
        return self._get_stored_note_from_dynamodb_note(note)

    def _get_dynamodb_note(self, note_id: str):
        try:
            note = DynamoDBNote.get(hash_key=self.identity.identity_id, range_key=f'note_{note_id}')
        except DynamoDBNote.DoesNotExist:
            raise AWSServicesException(recommended_status_code=404, detail=f'Note with id {note_id} not found')
        return note

    def _get_stored_note_from_dynamodb_note(self, note):
        return StoredNote(title=note.title, text=note.text,
                          note_id=self._get_stored_note_id_from_range_key(note.contents))

    def _get_stored_note_id_from_range_key(self, range_key):
        return range_key[len(self._get_note_id_prefix()):]

    @staticmethod
    def _get_range_key_from_note_id(note_id):
        return f'note_{note_id}'

    @staticmethod
    def _get_note_id_prefix():
        return 'note_'
