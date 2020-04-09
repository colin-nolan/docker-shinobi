from typing import Dict, Optional, Callable

import pytest
import testaid
from shinobi_client import ShinobiClient
from testinfra.host import Host

from .._common import run_ansible, create_example_email_and_password

testinfra_hosts = testaid.hosts()


def _run_ansible_shinobi_user_task(host: Host, testvars: Dict, *, email: Optional[str] = None,
                                   password: Optional[str] = None, state: Optional[str] = None) -> Dict:
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


@pytest.fixture
def does_user_exist(shinobi_client) -> Callable[[str], bool]:
    """
    TODO
    :param shinobi_client:
    :return:
    """
    def wrapped(email: str):
        # return _does_user_exist(shinobi_client, email)
        return shinobi_client.user.get(email) is not None

    return wrapped


@pytest.fixture
def shinobi_client(testvars: Dict):
    """
    TODO
    :param testvars:
    :return:
    """
    # TODO: common host string
    return ShinobiClient("0.0.0.0", testvars["shinobi_host_port"], testvars["shinobi_super_user_token"])


@pytest.fixture
def exiting_user(host: Host, testvars: Dict, shinobi_client):
    """
    TODO
    :param host:
    :param testvars:
    :param shinobi_client:
    :return:
    """
    email, password = create_example_email_and_password()
    return shinobi_client.user.create(email=email, password=password)


def test_create_user(host: Host, testvars: Dict, does_user_exist: Callable[[str], bool]):
    email, password = create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert result["changed"]
    assert does_user_exist(email)

    # Testing idempotence
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert not result["changed"]
    assert does_user_exist(email)


def test_list_non_existent_user(host: Host, testvars: Dict):
    email, password = create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email)
    assert not result["changed"]
    assert result["user"] is None


def test_list_user(host: Host, testvars: Dict, exiting_user: Dict):
    email = exiting_user["email"]
    result = _run_ansible_shinobi_user_task(host, testvars, email=email)
    assert not result["changed"]
    assert result["user"]["mail"] == email


def test_list_users(host: Host, testvars: Dict, shinobi_client: ShinobiClient):
    emails = []
    for i in range(3):
        email, password = create_example_email_and_password()
        shinobi_client.user.create(email=email, password=password)
        emails.append(email)

    result = _run_ansible_shinobi_user_task(host, testvars)
    assert not result["changed"]
    retrieved_users = tuple(filter(lambda user: user["mail"] in emails, result["users"]))
    assert len(retrieved_users) == len(emails)


def test_delete_non_existent_user(host: Host, testvars: Dict):
    email, _ = create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, state="absent")
    assert not result["changed"]


def test_delete_user(host: Host, testvars: Dict, exiting_user: Dict, does_user_exist: Callable[[str], bool]):
    email = exiting_user["mail"]
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, state="absent")
    assert result["changed"]
    assert not does_user_exist(email)


def test_modify_non_existent_user(host: Host, testvars: Dict, does_user_exist: Callable[[str], bool]):
    email, password = create_example_email_and_password()
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert result["changed"]
    assert does_user_exist(email)


def test_modify_user_with_same_values(
        host: Host, testvars: Dict, exiting_user: Dict, does_user_exist: Callable[[str], bool]):
    email = exiting_user["email"]
    password = exiting_user["password"]
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert not result["changed"]
    assert does_user_exist(email)


def test_modify_user_with_different_email(
        host: Host, testvars: Dict, exiting_user: Dict, does_user_exist: Callable[[str], bool]):
    email = exiting_user["email"]
    password = "new_password"
    result = _run_ansible_shinobi_user_task(host, testvars, email=email, password=password, state="present")
    assert result["changed"]
    assert does_user_exist(email)
