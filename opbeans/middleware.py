import uuid

import elasticapm


def tag_request_id_middleware(get_response):
    def middleware(request):
        elasticapm.tag(request_id=str(uuid.uuid4()))
        response = get_response(request)
        return response
    return middleware