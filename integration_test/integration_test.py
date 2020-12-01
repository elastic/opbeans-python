import time

import pytest
import requests

from requests.exceptions import ConnectionError


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def opbeans_python(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = "8000"
    url = f"http://{docker_ip}"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(f"{url}:{port}")
    )
    return url


def test_status_code_ui(opbeans_python):
    status = 200
    response = requests.get(opbeans_python + f":8000/dashboard/{status}")
    # curl -I 8000: 200 OK
    assert response.status_code == status


def test_status_code_elasticsearch(opbeans_python):
    status = 200
    response = requests.get(opbeans_python + ":9200")
    # curl -I 9200: 200 OK
    assert response.status_code == status


def test_status_code_redis(opbeans_python):
    time.sleep(150)
    status = 200
    response = requests.get(opbeans_python + ":5601")
    # curl -I 5601: 200 OK
    assert response.status_code == status
