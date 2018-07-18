import uuid
import random
from collections import namedtuple

import elasticapm


User = namedtuple('User', ['is_authenticated', 'id', 'username', 'email', 'customer_tier'])

users = [
    User(True, 1, 'wendy95', 'wendy95@walter-lee.org', '$$$$'),
    User(True, 2, 'qlopez', 'qlopez@galvan-vasquez.net', '$$$$'),
    User(True, 3, 'robert31', 'robert31@bullock.net', '$'),
    User(True, 4, 'ooneal', 'ooneal@barnett.com', '$'),
    User(True, 5, 'ryan54', 'ryan54@harding.org', '$$$$'),
    User(True, 6, 'tannermonica', 'tannermonica@burton-davis.com', '$$$$'),
    User(True, 7, 'aliciarichardson', 'aliciarichardson@carter-moore.com', '$'),
    User(True, 8, 'newmananthony', 'newmananthony@jones.net', '$$'),
    User(True, 9, 'timothy77', 'timothy77@ward.com', '$$$$'),
    User(True, 10, 'destiny36', 'destiny36@williams.org', '$$$'),
    User(True, 11, 'crystal68', 'crystal68@gonzales-horn.info', '$$'),
    User(True, 12, 'matthew21', 'matthew21@hernandez-travis.org', '$'),
    User(True, 13, 'michelle74', 'michelle74@barnes.net', '$$$'),
    User(True, 14, 'kimchy', 'kimchy@elastic.co', '$$$$'),
    User(True, 15, 'jeremy19', 'jeremy19@perry-west.com', '$'),
    User(True, 16, 'stevensvirginia', 'stevensvirginia@white-riggs.com', '$'),
    User(True, 17, 'jose52', 'jose52@barrett.com', '$'),
    User(True, 18, 'patrick89', 'patrick89@smith.com', '$$$$'),
    User(True, 19, 'michael18', 'michael18@cross.com', '$'),
    User(True, 20, 'danny42', 'danny42@greer-wilson.com', '$$'),
]

weights = [68, 70, 9, 55, 47, 76, 65, 96, 99, 14, 60, 34, 40, 15, 43, 31, 77, 40, 34, 88]


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
            request.user = random.choices(users, weights=weights)[0]
            elasticapm.tag(customer_tier=request.user.customer_tier)
        return get_response(request)
    return middleware
