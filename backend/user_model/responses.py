"""
Definition of responses
"""
CODE_SUCCESS = 0

RESPONSE_SUCCESS = {'message': 'success', 'code': CODE_SUCCESS}
RESPONSE_INVALID_FORM = {'message': 'Invalid form', 'code': 1}
RESPONSE_INVALID_USERNAME_OR_PASSWORD = {'message': 'Invalid username or password', 'code': 2}
RESPONSE_USERNAME_ALREADY_EXISTS = {'message': 'Username already exists', 'code': 3}
RESPONSE_INVALID_TOKEN = {'message': 'Invalid token', 'code': 4}
