class AWSServicesException(Exception):
    def __init__(self, recommended_status_code: int, detail: str):
        self.recommended_status_code = recommended_status_code
        self.detail = detail
