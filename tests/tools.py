import json
from os import path

from mailupy import Mailupy


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return json.loads(self.text)


def mock_request(res_type, url, *args, **kwargs):
    if Mailupy.AUTH_URL in url:
        return MockResponse(json.dumps({
            'access_token': '',
            'refresh_token': ''
        }))
    new_url = url.replace(Mailupy.BASE_URL, '')[1:].split('?')[0]

    file = open(path.join('tests', 'resources', *new_url.split('/'), f'{res_type}.json'))
    response = MockResponse(file.read())
    file.close()
    return response


def mock_request_refresh_token(method, url, *args, **kwargs):
    if Mailupy.AUTH_URL in url:
        return MockResponse(json.dumps({
            'access_token': 'good_token',
            'refresh_token': 'good_token'
        }), status_code=200)
    elif Mailupy.BASE_URL in url and kwargs['headers']['Authorization'] == 'Bearer bad_token':
        return MockResponse('', status_code=401)
    return mock_request('GET', url, *args, **kwargs)


def mock_request_400(method, url, *args, **kwargs):
    if Mailupy.AUTH_URL in url:
        return MockResponse(json.dumps({
            'access_token': 'good_token',
            'refresh_token': 'good_token'
        }), status_code=200)
    elif Mailupy.BASE_URL in url:
        return MockResponse(json.dumps({
            'ErrorDescription': 'Generic Error',
        }), status_code=400)
    return mock_request('GET', url, *args, **kwargs)


def mock_requests_error(method, url, *args, **kwargs):
    raise Exception('Connection Error')
