from types import MappingProxyType
from typing import Dict, Optional, Tuple
from uuid import uuid4

import pytest
import testaid
from testinfra.host import Host

DEFAULT_RUN_CONFIGURATION = dict(check=False)

testinfra_hosts = testaid.hosts()


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


def _run_ansible_shinobi_user_task(host: Host, testvars: Dict, *, email: Optional[str] = None,
                                   password: Optional[str] = None, state: Optional[str] = None) \
        -> Dict:
    """
    TODO
    :param host:
    :param testvars:
    :param email:
    :param password:
    :param state:
    :return:
    """
    parameter_arguments = {
        "host": "0.0.0.0",
        "port": testvars["shinobi_host_port"],
        "token": testvars["shinobi_super_user_token"]
    }
    if email is not None:
        parameter_arguments["email"] = email
    if password is not None:
        parameter_arguments["password"] = password
    if state is not None:
        parameter_arguments["state"] = state

    output = run_ansible(host, "shinobi_user", parameter_arguments)
    if output.get("user"):
        assert output["user"].get("user") is None, f"User data nested in output, when arguments: {parameter_arguments}"
    return output


def _create_example_email_and_password() -> Tuple[str, str]:
    """
    TODO
    :return:
    """
    random_string = str(uuid4())
    return f"{random_string}@example.com", random_string


def _does_user_exist(host: Host, testvars: Dict, email: str) -> bool:
    """
    TODO
    :param email:
    :param host:
    :param testvars:
    :return:
    """
    result = _run_ansible_shinobi_user_task(host, testvars, email=email)
    assert not result["changed"]
    return result["user"] is not None


@pytest.fixture
def exiting_user(host: Host, testvars: Dict):
    email, password = _create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert result["changed"]
    assert _does_user_exist(host, testvars, email)
    return result["user"]


def test_create_user(host: Host, testvars: Dict):
    email, password = _create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert result["changed"]
    assert _does_user_exist(host, testvars, email)

    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert not result["changed"]
    assert _does_user_exist(host, testvars, email)


def test_list_users(host: Host, testvars: Dict):
    emails = []
    for i in range(3):
        email, password = _create_example_email_and_password()
        result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
        assert result["changed"]
        emails.append(email)

    result = _run_ansible_shinobi_user_task(host, testvars)
    assert not result["changed"]
    retrieved_users = tuple(filter(lambda user: user["mail"] in emails, result["users"]))
    assert len(retrieved_users) == len(emails)


def test_list_non_existent_user(host: Host, testvars: Dict):
    email, password = _create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email)
    assert not result["changed"]
    assert result["user"] is None
#
#
# def test_list_existing_user(host: Host, testvars: Dict):
#     email, password = _create_example_email_and_password()
#     result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
#     assert result["changed"]
#
#     result = _run_ansible_shinobi_user_task(host, testvars, email=email)
#     assert not result["changed"]
#     assert result["user"]["mail"] == email
#
#
# def test_delete_non_existent_user(host: Host, testvars: Dict):
#     email, _ = _create_example_email_and_password()
#     result = _run_ansible_shinobi_user_task(host, testvars, email=email, state="absent")
#     assert not result["changed"]
#
#
# def test_delete_existing_user(host: Host, testvars: Dict, exiting_user: Dict):
#     email = exiting_user["mail"]
#     result = _run_ansible_shinobi_user_task(host, testvars, email=email, state="absent")
#     assert result["changed"]
#     assert not _does_user_exist(host, testvars, email)
#
#
# # TODO: test modify user
# # def modify_user(host: Host, testvars: Dict):
# #     email, password = _create_example_email_and_password()
# #     _run_ansible_shinobi_user(host, testvars, email=email, password=password, state="present")
# #     assert _does_user_exist(host, testvars, email)
#
