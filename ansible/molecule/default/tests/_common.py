import json
import random
import string
from copy import copy
from types import MappingProxyType
from typing import Dict, Tuple

from testinfra.host import Host


DEFAULT_RUN_CONFIGURATION = dict(check=False)
SHINOBI_HOST = "0.0.0.0"


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
    extra_vars = run_configuration.get("extra_vars", {})

    # Hacking around "this task 'X' has extra params, which is only allowed in the following modules..." error, which
    # happens with complex arguments (list, dicts).
    # e.g. https://www.reddit.com/r/ansible/comments/72ntlu/ansible_adhoc_commands_with_dict_keys/dnn1zn9/
    #
    # Solution is implied:
    # https://github.com/philpep/testinfra/blob/4b7f67541bc85e88817ddcccbd91670cb05fcbbb/testinfra/modules/ansible.py#L96-L101
    for key, value in copy(parameter_values).items():
        if isinstance(value, dict) or isinstance(value, list):
            placeholder_name = generate_random_string()
            extra_vars[placeholder_name] = value
            parameter_values[key] = "{{ %s }}" % (placeholder_name, )

    # For some reason module args are passed though as a string. JSON dump did not work
    parameter_arguments = " ".join(f"{key}={value}" for key, value in parameter_values.items())

    return host.ansible(playbook, parameter_arguments, **run_configuration, extra_vars=extra_vars)


def create_example_email_and_password() -> Tuple[str, str]:
    """
    Creates a random email address and password.
    :return: tuple where the first element is the email address and the second is the password
    """
    random_string = generate_random_string()
    return f"{random_string}@example.com", random_string


def generate_random_string(length: int = 8) -> str:
    """
    Generates a short random string.
    :param length: length of generated string
    :return: generated string
    """
    alphabet = string.ascii_lowercase
    return "".join(random.choices(alphabet, k=length))


def create_parameter_arguments(testvars: Dict, **kwargs) -> Dict:
    """
    TODO
    :param testvars:
    :param kwargs:
    :return:
    """
    parameter_arguments = {
        "host": SHINOBI_HOST,
        "port": testvars["shinobi_host_port"]
    }
    for key, value in kwargs.items():
        if value is not None:
            parameter_arguments[key] = value
    return parameter_arguments
