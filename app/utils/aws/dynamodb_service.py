import uuid

import boto3
from app.schemas import AWSIdentity, AWSIdentityCredentials


def create_note(identity: AWSIdentity, title: str, text: str):
    table = _get_table_resource(identity.credentials)
    note_id = f'{uuid.uuid4().hex}'
    note_dict = {
        'user_id': identity.identity_id,
        'contents': f'note_{note_id}',
        'title': title,
        'text': text
    }
    table.put_item(Item=note_dict)
    return note_id


def get_notes(identity: AWSIdentity):
    notes = table.query(KeyConditionExpression=f'user_id = :{identity.cognito_claims["sub"]} '
                                               f'AND begins_with(contents, note_')
    return notes


def delete_note(identity: AWSIdentity, note_id: str):
    table.delete_item(Key={'user_id': identity.cognito_claims['sub'],
                           'contents': f'note_{note_id}'})


def update_note(identity: AWSIdentity, note_id: str, title: str = None, text: str = None):
    attribute_updates = {}
    if title:
        attribute_updates['title'] = title
    if text:
        attribute_updates['text'] = text
    if not attribute_updates:
        return
    table.update_item(Key={'user_id': identity.cognito_claims['sub'],
                           'contents': f'note_{note_id}'},
                      AttributeUpdates=attribute_updates)


def _get_table_resource(credentials: AWSIdentityCredentials):
    session = boto3.Session(aws_access_key_id=credentials.access_key_id,
                            aws_secret_access_key=credentials.secret_key,
                            aws_session_token=credentials.session_token)
    dynamo_db = session.resource('dynamodb')
    table = dynamo_db.Table('fastnote-records')
    return table
