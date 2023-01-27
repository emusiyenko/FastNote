import uuid
import boto3
from botocore import exceptions as botocore_exceptions
from app.schemas import AWSIdentity, AWSIdentityCredentials
from boto3.dynamodb import conditions
from .aws_exception import AWSServicesException


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
    table = _get_table_resource(identity.credentials)
    query = conditions.Key('user_id').eq(identity.identity_id) & conditions.Key('contents').begins_with('note_')
    notes = table.query(KeyConditionExpression=query)['Items']
    result = []
    for note in notes:
        converted_note = _get_note_from_dynamo_db_item(note)
        result.append(converted_note)
    return result


def get_note(identity: AWSIdentity, note_id: str):
    table = _get_table_resource(identity.credentials)
    note = _call_table(table.get_item, Key={'user_id': identity.identity_id,
                                            'contents': f'note_{note_id}'})
    item = note.get('Item')
    if not item:
        raise AWSServicesException(recommended_status_code=404, detail=f'Note with id {note_id} not found')
    converted_note = _get_note_from_dynamo_db_item(item)
    return converted_note


def delete_note(identity: AWSIdentity, note_id: str):
    table = _get_table_resource(identity.credentials)
    _call_table(table.delete_item, Key={'user_id': identity.identity_id,
                                        'contents': f'note_{note_id}'})


def update_note(identity: AWSIdentity, note_id: str, title: str = None, text: str = None):
    table = _get_table_resource(identity.credentials)
    expression_attribute_values = {}
    expression_attribute_names = {}
    attribute_updates_expressions = []
    if title:
        attribute_updates_expressions.append('#title = :title')
        expression_attribute_values[':title'] = title
        expression_attribute_names['#title'] = 'title'
    if text:
        attribute_updates_expressions.append('#text = :text')
        expression_attribute_values[':text'] = text
        expression_attribute_names['#text'] = 'text'
    if not attribute_updates_expressions:
        return

    try:
        _call_table(table.update_item, Key={'user_id': identity.identity_id,
                                            'contents': f'note_{note_id}'},
                    UpdateExpression=f'SET {",".join(attribute_updates_expressions)}',
                    ExpressionAttributeValues=expression_attribute_values,
                    ExpressionAttributeNames=expression_attribute_names,
                    ConditionExpression='attribute_exists(user_id) and attribute_exists(contents)')
    except botocore_exceptions.ClientError:
        raise AWSServicesException(recommended_status_code=404, detail=f'Note with id {note_id} not found')


def _call_table(table_method, **kwargs):
    try:
        return table_method(**kwargs)
    except botocore_exceptions.ClientError as error:
        error_dict = error.response['Error']
        if error_dict['Code'] == 'ConditionalCheckFailedException':
            raise error
        else:
            raise AWSServicesException(recommended_status_code=400, detail=error_dict)


def _get_table_resource(credentials: AWSIdentityCredentials):
    session = boto3.Session(aws_access_key_id=credentials.access_key_id,
                            aws_secret_access_key=credentials.secret_key,
                            aws_session_token=credentials.session_token)
    dynamo_db = session.resource('dynamodb')
    table = dynamo_db.Table('fastnote-records')
    return table


def _get_note_from_dynamo_db_item(note: dict):
    note_copy = note.copy()
    note_copy['note_id'] = note['contents'].split('_')[1]
    note_copy.pop('contents')
    note_copy.pop('user_id')
    return note_copy
