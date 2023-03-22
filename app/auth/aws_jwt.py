import boto3
import logging
import cognitojwt
from app.settings import Settings
from app.schemas import AWSIdentity
from app.exceptions import AWSServicesException


def get_aws_identity(token: str) -> AWSIdentity:
    settings = Settings()
    identity_client = boto3.client('cognito-identity')
    user_pool_full_identifier = f'cognito-idp.{settings.aws_region}.amazonaws.com/{settings.cognito_user_pool_id}'
    try:
        id_response = identity_client.get_id(AccountId=settings.aws_account_id,
                                             IdentityPoolId=settings.cognito_identity_pool_id,
                                             Logins={
                                                 user_pool_full_identifier: token
                                             })
        identity_id = id_response['IdentityId']
        credentials = identity_client.get_credentials_for_identity(IdentityId=identity_id, Logins={
            user_pool_full_identifier: token
        })
    except identity_client.exceptions.NotAuthorizedException:
        raise AWSServicesException(recommended_status_code=401, detail="AWS exception: not authorized")
    except (identity_client.exceptions.ResourceNotFoundException,
            identity_client.exceptions.ResourceConflictException,
            identity_client.exceptions.TooManyRequestsException,
            identity_client.exceptions.LimitExceededException,
            identity_client.exceptions.InternalErrorException,
            identity_client.exceptions.ExternalServiceException,
            identity_client.exceptions.InvalidIdentityPoolConfigurationException,
            identity_client.exceptions.InvalidParameterException
            ) as ex:
        logging.error(ex)
        raise AWSServicesException(recommended_status_code=500, detail=repr(ex))

    try:
        claims = cognitojwt.decode(token, settings.aws_region, settings.cognito_user_pool_id,
                                   settings.cognito_client_id, testmode=False)
        identity_object = AWSIdentity.parse_obj(credentials)
        identity_object.cognito_claims = claims
    except Exception as ex:
        raise AWSServicesException(recommended_status_code=500, detail=repr(ex))

    return identity_object

