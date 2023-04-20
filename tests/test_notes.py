import json
from fastapi import status


class TestNotes:

    notes_base_url = '/v1/notes'

    def test_get_notes_unauthenticated(self, client):
        response = client.get(self.notes_base_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_notes(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()

        response = client.get(self.notes_base_url, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        notes = json.loads(response.content)
        assert len(notes) == 1

        note = notes[0]
        assert note['title'] == dynamodb_note.title and note['text'] == dynamodb_note.text and note['note_id'] == 'test'

    def test_get_note_unauthenticated(self, client):
        response = client.get(f'{self.notes_base_url}/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_note_wrong_id(self, logged_in_client, dynamo_db_table):
        client, headers, identity = logged_in_client
        response = client.get(f'{self.notes_base_url}/1', headers=headers)
        assert response.status_code == 404

    def test_get_note(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()

        response = client.get(f'{self.notes_base_url}/test', headers=headers)
        assert response.status_code == status.HTTP_200_OK

        note = json.loads(response.content)
        assert note['title'] == dynamodb_note.title and note['text'] == dynamodb_note.text and note['note_id'] == 'test'

    def test_create_note_unauthenticated(self, client):
        response = client.post(self.notes_base_url, json={'title': 'test', 'text': 'test_text'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_note(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client
        response = client.post(self.notes_base_url, json={'title': 'test', 'text': 'test_text'}, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

        note_dict = json.loads(response.content)
        note_id = note_dict['note_id']

        dynamo_db_notes = list(DynamoDBNote.query(hash_key=identity.identity_id,
                                                  range_key_condition=DynamoDBNote.contents == f'note_{note_id}'))
        assert len(dynamo_db_notes) == 1
        assert dynamo_db_notes[0].text == 'test_text'
        assert dynamo_db_notes[0].title == 'test'

    def test_put_note_unauthenticated(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.put(f'{self.notes_base_url}/test', json={'title': 'test-2', 'text': 'test_text-2'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_note_wrong_id(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.put(f'{self.notes_base_url}/1', json={'title': 'test-2', 'text': 'test_text-2'}, headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_note(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.put(f'{self.notes_base_url}/test', json={'title': 'test-2', 'text': 'test_text-2'}, headers=headers)

        dynamodb_note.refresh()
        assert response.status_code == status.HTTP_200_OK
        assert dynamodb_note.text == 'test_text-2'
        assert dynamodb_note.title == 'test-2'

    def test_patch_note_unauthenticated(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.patch(f'{self.notes_base_url}/test', json={'title': 'test-2'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_note_wrong_id(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.patch(f'{self.notes_base_url}/1', json={'title': 'test-2'}, headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_note(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.patch(f'{self.notes_base_url}/test', json={'title': 'test-2'}, headers=headers)

        dynamodb_note.refresh()
        assert response.status_code == status.HTTP_200_OK
        assert dynamodb_note.text == 'test_text'
        assert dynamodb_note.title == 'test-2'

    def test_delete_note_unauthenticated(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.delete(f'{self.notes_base_url}/test')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_note_wrong_id(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.delete(f'{self.notes_base_url}/1', headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_note(self, logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.delete(f'{self.notes_base_url}/test', headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        dynamo_db_notes = list(DynamoDBNote.query(hash_key=identity.identity_id,
                                                  range_key_condition=DynamoDBNote.contents == f'note_test'))

        assert len(dynamo_db_notes) == 0



