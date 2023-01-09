import boto3


def create_note(user_id: str, title: str, text: str, credentials: dict):
    client = boto3.client('dynamodb')



def get_notes(user_id: str): pass


def delete_note(user_id, note_id: str): pass


def update_note(user_id, note_id: str, title: str = None, text: str = None): pass
