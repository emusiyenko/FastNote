import json


class TestNotes:

    @staticmethod
    def test_get_notes_unauthenticated(client):
        response = client.get('/notes')
        assert response.status_code == 401

    @staticmethod
    def test_get_notes(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()

        response = client.get('/notes', headers=headers)
        assert response.status_code == 200

        notes = json.loads(response.content)
        assert len(notes) == 1

        note = notes[0]
        assert note['title'] == dynamodb_note.title and note['text'] == dynamodb_note.text and note['note_id'] == 'test'

