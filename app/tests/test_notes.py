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

    @staticmethod
    def test_get_note_unauthenticated(client):
        response = client.get('/notes/1')
        assert response.status_code == 401

    @staticmethod
    def test_get_note_wrong_id(logged_in_client, dynamo_db_table):
        client, headers, identity = logged_in_client
        response = client.get('/notes/1', headers=headers)
        assert response.status_code == 404

    @staticmethod
    def test_get_note(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()

        response = client.get('/notes/test', headers=headers)
        assert response.status_code == 200

        note = json.loads(response.content)
        assert note['title'] == dynamodb_note.title and note['text'] == dynamodb_note.text and note['note_id'] == 'test'

    @staticmethod
    def test_create_note_unauthenticated(client):
        response = client.post('/notes', json={'title': 'test', 'text': 'test_text'})
        assert response.status_code == 401

    @staticmethod
    def test_create_note(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client
        response = client.post('/notes', json={'title': 'test', 'text': 'test_text'}, headers=headers)
        assert response.status_code == 201

        note_dict = json.loads(response.content)
        note_id = note_dict['note_id']

        dynamo_db_notes = list(DynamoDBNote.query(hash_key=identity.identity_id,
                                                  range_key_condition=DynamoDBNote.contents == f'note_{note_id}'))
        assert len(dynamo_db_notes) == 1
        assert dynamo_db_notes[0].text == 'test_text'
        assert dynamo_db_notes[0].title == 'test'

    @staticmethod
    def test_put_note_unauthenticated(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.put('/notes/test', json={'title': 'test-2', 'text': 'test_text-2'})

        assert response.status_code == 401

    @staticmethod
    def test_put_note_wrong_id(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.put('/notes/1', json={'title': 'test-2', 'text': 'test_text-2'}, headers=headers)

        assert response.status_code == 404

    @staticmethod
    def test_put_note(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.put('/notes/test', json={'title': 'test-2', 'text': 'test_text-2'}, headers=headers)

        dynamodb_note.refresh()
        assert response.status_code == 200
        assert dynamodb_note.text == 'test_text-2'
        assert dynamodb_note.title == 'test-2'

    @staticmethod
    def test_patch_note_unauthenticated(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.patch('/notes/test', json={'title': 'test-2'})

        assert response.status_code == 401

    @staticmethod
    def test_patch_note_wrong_id(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.patch('/notes/1', json={'title': 'test-2'}, headers=headers)

        assert response.status_code == 404

    @staticmethod
    def test_patch_note(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.patch('/notes/test', json={'title': 'test-2'}, headers=headers)

        dynamodb_note.refresh()
        assert response.status_code == 200
        assert dynamodb_note.text == 'test_text'
        assert dynamodb_note.title == 'test-2'

    @staticmethod
    def test_delete_note_unauthenticated(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.delete('/notes/test')

        assert response.status_code == 401

    @staticmethod
    def test_delete_note_wrong_id(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.delete('/notes/1', headers=headers)

        assert response.status_code == 404

    @staticmethod
    def test_delete_note(logged_in_client, dynamo_db_table):
        from app.utils.dynamodb_service import DynamoDBNote
        client, headers, identity = logged_in_client

        dynamodb_note = DynamoDBNote(identity.identity_id,
                                     contents='note_test',
                                     title='test_title', text='test_text')
        dynamodb_note.save()
        response = client.delete('/notes/test', headers=headers)
        assert response.status_code == 204

        dynamo_db_notes = list(DynamoDBNote.query(hash_key=identity.identity_id,
                                                  range_key_condition=DynamoDBNote.contents == f'note_test'))

        assert len(dynamo_db_notes) == 0



