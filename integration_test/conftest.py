import contextlib
import os
import subprocess
import time
import timeit

import attr

import pytest


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "", "docker-compose.yml")


@pytest.fixture(scope="session")
def url():
    return "http://127.0.0.1:8000/dashboard"


@pytest.fixture(scope="session")
def docker_ip():
    return "127.0.0.1"

@pytest.fixture(scope="session")
def portlist():
    return [
        "8000",
        "9200",
        "6379"
    ]


def execute(command, success_codes=(0,)):
    """Run a shell command."""
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        status = 0
    except subprocess.CalledProcessError as error:
        output = error.output or b""
        status = error.returncode
        command = error.cmd

    if status not in success_codes:
        raise Exception(
            'Command {} returned {}: """{}""".'.format(
                command, status, output.decode("utf-8")
            )
        )
    return output


@attr.s(frozen=True)
class Services:

    _docker_compose = attr.ib()
    _services = attr.ib(init=False, default=attr.Factory(dict))

    def port_for(self, service, container_port):
        """Return the "host" port for `service` and `container_port`.
        E.g. If the service is defined like this:
            version: '2'
            services:
              httpbin:
                build: .
                ports:
                  - "8000:80"
        this method will return 8000 for container_port=80.
        """

        # Lookup in the cache.
        cache = self._services.get(service, {}).get(container_port, None)
        if cache is not None:
            return cache

        output = self._docker_compose.execute("port %s %d" % (service, container_port))
        endpoint = output.strip().decode("utf-8")
        if not endpoint:
            raise ValueError(
                'Could not detect port for "%s:%d".' % (service, container_port)
            )

        # Usually, the IP address here is 0.0.0.0, so we don't use it.
        match = int(endpoint.split(":", 1)[1])

        # Store it in cache in case we request it multiple times.
        self._services.setdefault(service, {})[container_port] = match

        return match

    def wait_until_responsive(self, check, timeout, pause, clock=timeit.default_timer):
        """Wait until a service is responsive."""

        ref = clock()
        now = ref
        while (now - ref) < timeout:
            if check():
                return
            time.sleep(pause)
            now = clock()

        raise Exception("Timeout reached while waiting on service!")


def str_to_list(arg):
    if isinstance(arg, (list, tuple)):
        return arg
    return [arg]


@attr.s(frozen=True)
class DockerComposeExecutor:

    _compose_files = attr.ib(converter=str_to_list)
    _compose_project_name = attr.ib()

    def execute(self, subcommand):
        command = "docker-compose"
        for compose_file in self._compose_files:
            command += ' -f "{}"'.format(compose_file)
        command += ' -p "{}" {}'.format(self._compose_project_name, subcommand)
        return execute(command)


@pytest.fixture(scope="session")
def docker_compose_project_name():
    """Generate a project name using the current process PID. Override this
    fixture in your tests if you need a particular project name."""

    return "pytest{}".format(os.getpid())


@contextlib.contextmanager
def get_docker_services(docker_compose_file, docker_compose_project_name):
    docker_compose = DockerComposeExecutor(
        docker_compose_file, docker_compose_project_name
    )

    # Spawn containers.
    docker_compose.execute("up --build -d")

    # Let test(s) run.
    yield Services(docker_compose)

    # Clean up.
    docker_compose.execute("down -v")


@pytest.fixture(scope="session")
def docker_services(docker_compose_file, docker_compose_project_name):
    """Start all services from a docker compose file (`docker-compose up`).
    After test are finished, shutdown all services (`docker-compose down`)."""

    with get_docker_services(
        docker_compose_file, docker_compose_project_name
    ) as docker_service:
        yield docker_service
