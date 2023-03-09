import json
import os
import boto3
import pytest

from pathlib import Path
from dotenv import load_dotenv
from moto import mock_cognitoidp
from ..settings import Settings
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def aws_credentials():
    load_dotenv(dotenv_path=Path('app/tests/.test.env'))


@pytest.fixture(scope="function")
def cognito_idp(aws_credentials):
    with mock_cognitoidp():
        settings = Settings()
        cognito_service = boto3.client('cognito-idp')
        user_pool_id = cognito_service.create_user_pool(PoolName='test_pool')["UserPool"]["Id"]
        user_pool_client_id = cognito_service.create_user_pool_client(
            UserPoolId=user_pool_id, ClientName='test_client', CallbackURLs=['test_callback']
        )['UserPoolClient']['ClientId']
        cognito_service.create_group(GroupName=settings.cognito_regular_user_group_name,
                                     UserPoolId=user_pool_id)
        os.environ['COGNITO_USER_POOL_ID'] = user_pool_id
        os.environ['COGNITO_CLIENT_ID'] = user_pool_client_id
        yield cognito_service, user_pool_id


@pytest.fixture(scope="function")
def client(aws_credentials):
    from ..main import app
    client = TestClient(app)
    return client


def test_sign_up_success(client, cognito_idp):
    cognito_service, user_pool_id = cognito_idp
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


def test_sign_up_user_exists(client, cognito_idp):
    cognito_service, user_pool_id = cognito_idp
    body = {
        'username': 'test',
        'password': ":MMm123456!",
        'email': 'test@test.com'
    }
    cognito_service.admin_create_user(UserPoolId=user_pool_id, Username='test')
    response = client.post('/auth/sign_up', json=body)
    assert response.status_code == 400
    body = json.loads(response.content)
    assert body == {'detail': "Username already exists"}

