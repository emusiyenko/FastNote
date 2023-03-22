class TestNotes:

    @staticmethod
    def test_get_notes_unauthenticated(client):
        response = client.get('/notes')
        assert response.status_code == 401

    @staticmethod
    def test_get_notes(logged_in_client):
        client, headers = logged_in_client
        response = client.get('/notes', headers=headers)
        assert response.status_code == 200
