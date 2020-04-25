from typing import Dict, Callable

import pytest
from shinobi_client import ShinobiClient
from testinfra.host import Host

from .._common import run_ansible, create_example_email_and_password, SHINOBI_HOST, create_parameter_arguments

import takeltest

testinfra_hosts = takeltest.hosts()


@pytest.fixture
def shinobi_user_ansible_task_runner(host: Host, testvars: Dict) -> Callable[..., Dict]:
    """
    TODO
    :param host:
    :param testvars:
    :param kwargs:
    :return:
    """
    def wrapped(**kwargs) -> Dict:
        parameter_arguments = create_parameter_arguments(testvars, token=testvars["shinobi_super_user_token"], **kwargs)
        output = run_ansible(host, "shinobi_user", parameter_arguments)
        if output.get("user"):
            assert output["user"].get("user") is None, \
                f"User data nested in output, when arguments: {parameter_arguments}"
        return output

    return wrapped


@pytest.fixture
def does_user_exist(shinobi_client: ShinobiClient) -> Callable[[str], bool]:
    """
    TODO
    :param shinobi_client:
    :return:
    """
    def wrapped(email: str):
        # return _does_user_exist(shinobi_client, email)
        return shinobi_client.user.get(email) is not None

    return wrapped


def test_create_user(shinobi_user_ansible_task_runner, does_user_exist):
    email, password = create_example_email_and_password()
    result = shinobi_user_ansible_task_runner(email=email, password=password, state="present")
    assert result["changed"]
    assert does_user_exist(email)

    # Testing idempotence
    result = shinobi_user_ansible_task_runner(email=email, password=password, state="present")
    assert not result["changed"]
    assert does_user_exist(email)


def test_list_non_existent_user(shinobi_user_ansible_task_runner):
    email, password = create_example_email_and_password()
    result = shinobi_user_ansible_task_runner(email=email)
    assert not result["changed"]
    assert result["user"] is None


def test_list_user(shinobi_user_ansible_task_runner, existing_user):
    email = existing_user["email"]
    result = shinobi_user_ansible_task_runner(email=email)
    assert not result["changed"]
    assert result["user"]["mail"] == email


def test_list_users(shinobi_user_ansible_task_runner, shinobi_client: ShinobiClient):
    emails = []
    for i in range(3):
        email, password = create_example_email_and_password()
        shinobi_client.user.create(email=email, password=password)
        emails.append(email)

    result = shinobi_user_ansible_task_runner()
    assert not result["changed"]
    retrieved_users = tuple(filter(lambda user: user["mail"] in emails, result["users"]))
    assert len(retrieved_users) == len(emails)


def test_modify_non_existent_user(shinobi_user_ansible_task_runner, does_user_exist):
    email, password = create_example_email_and_password()
    result = shinobi_user_ansible_task_runner(email=email, password=password, state="present")
    assert result["changed"]
    assert does_user_exist(email)


def test_modify_user_with_same_values(shinobi_user_ansible_task_runner, existing_user, does_user_exist):
    email = existing_user["email"]
    password = existing_user["password"]
    result = shinobi_user_ansible_task_runner(email=email, password=password, state="present")
    assert not result["changed"]
    assert does_user_exist(email)


def test_modify_user_with_different_email(shinobi_user_ansible_task_runner, existing_user, does_user_exist):
    email = existing_user["email"]
    password = "new_password"
    result = shinobi_user_ansible_task_runner(email=email, password=password, state="present")
    assert result["changed"]
    assert does_user_exist(email)


def test_delete_non_existent_user(shinobi_user_ansible_task_runner):
    email, _ = create_example_email_and_password()
    result = shinobi_user_ansible_task_runner(email=email, state="absent")
    assert not result["changed"]


def test_delete_user(shinobi_user_ansible_task_runner, existing_user, does_user_exist):
    email = existing_user["mail"]
    result = shinobi_user_ansible_task_runner(email=email, state="absent")
    assert result["changed"]
    assert not does_user_exist(email)
