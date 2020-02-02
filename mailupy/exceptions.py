class MailupyException(Exception):
    pass


class MailupyRequestException(MailupyException):
    def __init__(self, response):
        super(MailupyException, self).__init__(
            f"Error {response.status_code} - {response.json()['ErrorDescription']}"
        )
