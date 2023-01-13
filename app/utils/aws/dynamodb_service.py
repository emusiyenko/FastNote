import boto3
from app.schemas import AWSIdentity


def create_note(identity: AWSIdentity, title: str, text: str):
    client = boto3.client('dynamodb')



def get_notes(user_id: str): pass


def delete_note(user_id, note_id: str): pass


def update_note(user_id, note_id: str, title: str = None, text: str = None): pass
