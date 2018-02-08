import uuid
import random
from collections import namedtuple

import elasticapm


User = namedtuple('User', ['is_authenticated', 'id', 'username', 'email'])

users = [
    User(True, 1, 'arthurdent', 'arthur.dent@example.com'),
    User(True, 2, 'fprefect', 'ford.prefect@example.com'),
    User(True, 3, 'trillian', 'adastra@example.com'),
    User(True, 4, 'zaphod', 'z@example.com'),
]


def tag_request_id_middleware(get_response):
    def middleware(request):
        __traceback_hide__ = True
        elasticapm.tag(request_id=str(uuid.uuid4()))
        response = get_response(request)
        return response
    return middleware


def user_middleware(get_response):
    def middleware(request):
        __traceback_hide__ = True
        if not request.user.is_authenticated:
            request.user = random.choice(users)
        return get_response(request)
    return middleware
