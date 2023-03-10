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
    success = load_dotenv(dotenv_path=Path('.test.env'))
    return success


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
    from app.main import app
    client = TestClient(app)
    return client


@pytest.fixture(scope="function")
def cognito_idp_with_new_user(cognito_idp):
    cognito_service, user_pool_id = cognito_idp
    settings = Settings()

    username = "Test"
    password = "Passw0rd!"
    client_id = settings.cognito_client_id
    cognito_service.sign_up(ClientId=client_id, Username=username, Password=password)
    return cognito_service, user_pool_id, username, password


@pytest.fixture(scope="function")
def cognito_idp_with_confirmed_user(cognito_idp_with_new_user):
    cognito_service, user_pool_id, username, password = cognito_idp_with_new_user
    cognito_service.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=username)
    return cognito_service, user_pool_id, username, password
