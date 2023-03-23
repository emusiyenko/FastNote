import os
import boto3
import pytest
import json
import importlib

from pathlib import Path
from dotenv import load_dotenv
from moto import mock_cognitoidp, mock_dynamodb
from app.settings import Settings
from fastapi.testclient import TestClient
from moto.cognitoidentity.models import CognitoIdentityBackend
from moto.core.base_backend import BackendDict
from moto.core.models import base_decorator
from moto.cognitoidentity.urls import url_bases, url_paths

"""
Default backend generates new identity each time it's requested by get_id.
On the other hand identity_id is the hash key in dynamo and must be stable for a single user.
The code below replaces the default backend by a custom one
"""


class StaticCognitoIdentityBackend(CognitoIdentityBackend):
    def get_id(self, identity_pool_id: str) -> str:
        identity_id = f"{self.region_name}:123456789"
        identity_id_dict = {"IdentityId": identity_id}
        if not len(self.pools_identities[identity_pool_id]["Identities"]):
            self.pools_identities[identity_pool_id]["Identities"].append(identity_id_dict)
        return json.dumps(identity_id_dict)


cognitoidentity_backends = BackendDict(StaticCognitoIdentityBackend, "cognito-identity")
cognito_responses_module = importlib.import_module('moto.cognitoidentity.responses')
setattr(cognito_responses_module, 'cognitoidentity_backends', cognitoidentity_backends)
setattr(cognito_responses_module, 'CognitoIdentityBackend', StaticCognitoIdentityBackend)


@pytest.fixture(scope="function")
def aws_credentials():
    success = load_dotenv(dotenv_path=Path('.test.env'))
    return success


@pytest.fixture(scope="function")
def cognito_idp(aws_credentials):
    with mock_cognitoidp():
        mock = base_decorator(cognitoidentity_backends)()
        mock.start()
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

        cognito_identity_service = boto3.client('cognito-identity')
        response = cognito_identity_service.create_identity_pool(IdentityPoolName='test_identity_pool',
                                                                 AllowUnauthenticatedIdentities=False)
        os.environ['COGNITO_IDENTITY_POOL_ID'] = response['IdentityPoolId']

        yield cognito_service, user_pool_id
        mock.stop()


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


@pytest.fixture(scope="function")
def logged_in_client(client, cognito_idp_with_confirmed_user):
    from app.auth.aws_jwt import get_aws_identity
    cognito_service, user_pool_id, username, password = cognito_idp_with_confirmed_user
    response = client.post(f'/auth/sign_in', data={"username": username, "password": password})
    assert response.status_code == 200
    body = json.loads(response.content)
    access_token = body['access_token']
    identity = get_aws_identity(access_token)
    return client, {"Authorization": f"Bearer {access_token}"}, identity


@pytest.fixture(scope="function")
def dynamo_db_table(aws_credentials):
    with mock_dynamodb():
        settings = Settings()
        dynamodb_resource = boto3.resource('dynamodb')
        dynamodb_resource.create_table(TableName=settings.dynamo_db_notes_table,
                                       AttributeDefinitions=[
                                           {
                                               'AttributeName': 'user_id',
                                               'AttributeType': 'S'
                                           },
                                           {
                                               'AttributeName': 'contents',
                                               'AttributeType': 'S'
                                           }
                                       ],
                                       KeySchema=[
                                           {
                                               'AttributeName': 'user_id',
                                               'KeyType': 'HASH'
                                           },
                                           {
                                               'AttributeName': 'contents',
                                               'KeyType': 'RANGE'
                                           }
                                       ],
                                       BillingMode='PAY_PER_REQUEST')
        table = dynamodb_resource.Table(settings.dynamo_db_notes_table)
        yield table
