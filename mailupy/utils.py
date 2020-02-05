import requests


type_to_request_function = {
    'GET': requests.get,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete
}
