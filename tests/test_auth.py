import json
from fastapi import status


class TestAuth:

    @staticmethod
    def test_sign_up_success(client, cognito_idp):
        cognito_service, user_pool_id = cognito_idp
        body = {
            'username': 'test',
            'password': ":MMm123456!",
            'email': 'test@test.com'
        }
        response = client.post('/auth/sign_up', json=body)
        assert response.status_code == status.HTTP_201_CREATED
        user = cognito_service.admin_get_user(UserPoolId=user_pool_id, Username='test')
        user_name = [d['Value'] for d in user['UserAttributes'] if d['Name'] == 'name'][0]
        user_email = [d['Value'] for d in user['UserAttributes'] if d['Name'] == 'email'][0]

        assert user_name == 'test'
        assert user_email == 'test@test.com'

    @staticmethod
    def test_sign_up_user_exists(client, cognito_idp):
        cognito_service, user_pool_id = cognito_idp
        body = {
            'username': 'test',
            'password': ":MMm123456!",
            'email': 'test@test.com'
        }
        cognito_service.admin_create_user(UserPoolId=user_pool_id, Username='test')
        response = client.post('/auth/sign_up', json=body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = json.loads(response.content)
        assert body == {'detail': "Username already exists"}

    @staticmethod
    def test_sign_up_wrong_password(client, cognito_idp):
        body = {
            'username': 'test',
            'password': ":123",
            'email': 'test@test.com'
        }
        response = client.post('/auth/sign_up', json=body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = json.loads(response.content)
        assert body == {'detail': "Password is invalid"}

    @staticmethod
    def test_sign_in_success(client, cognito_idp_with_confirmed_user):
        cognito_service, user_pool_id, username, password = cognito_idp_with_confirmed_user
        response = client.post(f'/auth/sign_in', data={"username": username, "password": password})
        assert response.status_code == status.HTTP_200_OK
        body = json.loads(response.content)

        assert 'access_token' in body
        assert 'refresh_token' in body
        assert 'expires_in' in body
        assert 'token_type' in body
        assert body['token_type'] == "Bearer"

    @staticmethod
    def test_sign_in_invalid_password(client, cognito_idp_with_confirmed_user):
        cognito_service, user_pool_id, username, password = cognito_idp_with_confirmed_user
        response = client.post(f'/auth/sign_in', data={"username": username, "password": password + "_invalid"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        body = json.loads(response.content)
        assert body == {'detail': "Not authorized"}

    @staticmethod
    def test_sign_in_invalid_username(client, cognito_idp_with_confirmed_user):
        cognito_service, user_pool_id, username, password = cognito_idp_with_confirmed_user
        response = client.post(f'/auth/sign_in', data={"username": username + "_invalid",
                                                       "password": password})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        body = json.loads(response.content)
        assert body == {'detail': "User not found"}

    @staticmethod
    def test_sign_in_user_not_confirmed_success(client, cognito_idp_with_new_user):
        cognito_service, user_pool_id, username, password = cognito_idp_with_new_user
        response = client.post(f'/auth/sign_in', data={"username": username, "password": password})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = json.loads(response.content)
        assert body == {'detail': "User not confirmed"}

    @staticmethod
    def test_confirm_user(client, cognito_idp_with_new_user):
        cognito_service, user_pool_id, username, password = cognito_idp_with_new_user
        response = client.post(f'/auth/confirm_sign_up?username={username}&confirmation_code=12345678')
        assert response.status_code == status.HTTP_200_OK

        user = cognito_service.admin_get_user(UserPoolId=user_pool_id, Username=username)
        assert user['UserStatus'] == 'CONFIRMED'







