import boto3
import hmac, hashlib, base64
from app.settings import Settings
from .aws_exception import AWSServicesException

client = boto3.client('cognito-idp')
settings = Settings()


def sign_up(username: str, password: str, email: str):
    _call_client(client.sign_up,
                 ClientId=settings.cognito_client_id,
                 Username=username,
                 Password=password,
                 SecretHash=_generate_secret_hash(username),
                 UserAttributes=[
                     {
                         'Name': 'email',
                         'Value': email
                     },
                     {
                         'Name': 'name',
                         'Value': username
                     }
                 ]
                 )


def add_user_to_default_group(username: str):
    _call_client(client.admin_add_user_to_group,
                 UserPoolId=settings.cognito_user_pool_id,
                 Username=username,
                 GroupName=settings.cognito_regular_user_group_name)


def confirm_sign_up(username: str, confirmation_code: str):
    _call_client(client.confirm_sign_up,
                 ClientId=settings.cognito_client_id,
                 Username=username,
                 ConfirmationCode=confirmation_code,
                 SecretHash=_generate_secret_hash(username)
                 )


def initiate_auth(username: str, password: str):
    response = _call_client(client.initiate_auth,
                            AuthFlow='USER_PASSWORD_AUTH',
                            ClientId=settings.cognito_client_id,
                            AuthParameters={
                                'USERNAME': username,
                                'PASSWORD': password,
                                'SECRET_HASH': _generate_secret_hash(username)
                            })
    result = response['AuthenticationResult']
    return {
        'access_token': result['IdToken'],  # TODO: check
        'token_type': result['TokenType'],
        'refresh_token': result['RefreshToken'],
        'expires_in': result['ExpiresIn']
    }


def _call_client(method, **kwargs):
    try:
        return method(**kwargs)
    except (client.exceptions.ResourceNotFoundException,
            client.exceptions.InvalidParameterException,
            client.exceptions.UnexpectedLambdaException,
            client.exceptions.UserLambdaValidationException,
            client.exceptions.InvalidLambdaResponseException,
            client.exceptions.TooManyRequestsException,
            client.exceptions.TooManyFailedAttemptsException,
            client.exceptions.LimitExceededException,
            client.exceptions.AliasExistsException,
            client.exceptions.InternalErrorException,
            client.exceptions.InvalidSmsRoleAccessPolicyException,
            client.exceptions.InvalidSmsRoleTrustRelationshipException,
            client.exceptions.InvalidEmailRoleAccessPolicyException,
            client.exceptions.CodeDeliveryFailureException) as ex:
        raise AWSServicesException(recommended_status_code=500, detail=repr(ex))
    except client.exceptions.UsernameExistsException:
        raise AWSServicesException(recommended_status_code=400, detail="Username already exists")
    except client.exceptions.InvalidPasswordException:
        raise AWSServicesException(recommended_status_code=401, detail="Password is invalid")
    except client.exceptions.CodeMismatchException:
        raise AWSServicesException(recommended_status_code=401, detail="Provided code doesn't match")
    except client.exceptions.ExpiredCodeException:
        raise AWSServicesException(recommended_status_code=401, detail="Provided code has expired")
    except client.exceptions.PasswordResetRequiredException:
        raise AWSServicesException(recommended_status_code=401, detail="Password reset required")
    except client.exceptions.UserNotFoundException:
        raise AWSServicesException(recommended_status_code=401, detail="User not found")
    except client.exceptions.UserNotConfirmedException:
        raise AWSServicesException(recommended_status_code=401, detail="User not confirmed")
    except (client.exceptions.NotAuthorizedException,
            client.exceptions.ForbiddenException) as ex:
        raise AWSServicesException(recommended_status_code=401, detail=repr(ex))


def _generate_secret_hash(username):
    app_client_id = settings.cognito_client_id
    app_client_secret = settings.cognito_client_secret
    message = bytes(username + app_client_id, 'utf-8')
    key = bytes(app_client_secret, 'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
    return secret_hash
