import json
import os

import boto3

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from moto import mock_cognitoidp
from ..settings import Settings
from pathlib import Path

success = load_dotenv(dotenv_path=Path('app/tests/.test.env'))

from ..main import app

settings = Settings()


@mock_cognitoidp
def test_sign_up():
    cognito_service = boto3.client('cognito-idp')
    user_pool_id = cognito_service.create_user_pool(PoolName='test_pool')["UserPool"]["Id"]
    user_pool_client_id = cognito_service.create_user_pool_client(
        UserPoolId=user_pool_id, ClientName='test_client', CallbackURLs=['test_callback']
    )['UserPoolClient']['ClientId']
    user_group = cognito_service.create_group(GroupName=settings.cognito_regular_user_group_name,
                                              UserPoolId=user_pool_id)
    os.environ['COGNITO_USER_POOL_ID'] = user_pool_id
    os.environ['COGNITO_CLIENT_ID'] = user_pool_client_id
    client = TestClient(app)
    body = {
        'username': 'test',
        'password': ":MMm123456!",
        'email': 'test@test.com'
    }
    response = client.post('/auth/sign_up', json=body)
    assert response.status_code == 201
    user = cognito_service.admin_get_user(UserPoolId=user_pool_id, Username='test')
    user_name = [d['Value'] for d in user['UserAttributes'] if d['Name'] == 'name'][0]
    user_email = [d['Value'] for d in user['UserAttributes'] if d['Name'] == 'email'][0]

    assert user_name == 'test'
    assert user_email == 'test@test.com'

