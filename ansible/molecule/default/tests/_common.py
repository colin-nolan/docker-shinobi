from types import MappingProxyType
from typing import Dict, Tuple
from uuid import uuid4

from testinfra.host import Host

DEFAULT_RUN_CONFIGURATION = dict(check=False)


def run_ansible(host: Host, playbook: str, parameter_values: Dict, run_configuration: Dict = MappingProxyType({})) \
        -> Dict:
    """
    TODO
    :param host:
    :param playbook:
    :param parameter_values:
    :param run_configuration:
    :return:
    """
    run_configuration = dict(**DEFAULT_RUN_CONFIGURATION, **run_configuration)
    return host.ansible(
        playbook, " ".join(f"{key}={value}" for key, value in parameter_values.items()), **run_configuration)


def create_example_email_and_password() -> Tuple[str, str]:
    """
    Creates a random email address and password.
    :return: tuple where the first element is the email address and the second is the password
    """
    random_string = str(uuid4())
    return f"{random_string}@example.com", random_string
