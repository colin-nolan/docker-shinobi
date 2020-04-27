from typing import Dict, Callable

import pytest
import takeltest
from shinobi_client import ShinobiClient, ShinobiMonitorOrm
from testinfra.host import Host

from .resources.metadata import generate_monitor_configuration
from .._common import run_ansible, create_parameter_arguments, generate_random_string

testinfra_hosts = takeltest.hosts()


@pytest.fixture
def shinobi_monitor_ansible_task_runner(host: Host, testvars: Dict) -> Callable[..., Dict]:
    """
    TODO
    :param host:
    :param testvars:
    :return:
    """
    def wrapper(**kwargs) -> Dict:
        parameter_arguments = create_parameter_arguments(testvars, **kwargs)
        return run_ansible(host, "shinobi_monitor", parameter_arguments)

    return wrapper


@pytest.fixture
def does_monitor_exist(shinobi_client: ShinobiClient) -> Callable[[Dict, str], bool]:
    """
    TODO
    :param shinobi_client:
    :return:
    """
    def wrapped(user: Dict, monitor_id: str):
        return shinobi_client.monitor(user["email"], user["password"]).get(monitor_id) is not None

    return wrapped


def test_create_monitor(shinobi_monitor_ansible_task_runner, existing_user, shinobi_client: ShinobiClient):
    email = existing_user["email"]
    password = existing_user["password"]
    monitor_id = generate_random_string()
    configuration = generate_monitor_configuration()

    parameter_arguments = dict(
        email=email, password=password, state="present", id=monitor_id, configuration=configuration)

    result = shinobi_monitor_ansible_task_runner(**parameter_arguments)
    assert result["changed"]
    assert "details" in result["monitor"]

    shinobi_monitor_orm = shinobi_client.monitor(email, password)
    monitor = shinobi_monitor_orm.get(monitor_id)
    assert monitor is not None
    assert ShinobiMonitorOrm.is_configuration_equivalent(configuration, monitor)

    # Testing idempotence
    result = shinobi_monitor_ansible_task_runner(**parameter_arguments)
    assert not result["changed"]
    monitor = shinobi_monitor_orm.get(monitor_id)
    assert monitor is not None
    assert ShinobiMonitorOrm.is_configuration_equivalent(configuration, monitor)


def test_list_non_existent_monitor(shinobi_monitor_ansible_task_runner, existing_user):
    result = shinobi_monitor_ansible_task_runner(user=existing_user, monitor_id=generate_random_string())
    assert not result["changed"]
    assert result["monitor"] is None


def test_list_monitor(shinobi_monitor_ansible_task_runner, existing_monitor, existing_user):
    result = shinobi_monitor_ansible_task_runner(monitor_id=existing_monitor["id"], user=existing_user)
    assert not result["changed"]
    assert result["monitor"]["path"] == existing_monitor["path"]


def test_list_monitors(shinobi_monitor_ansible_task_runner, monitor_orm: ShinobiMonitorOrm, existing_user):
    monitor_ids = []
    for i in range(3):
        monitor_id = generate_random_string()
        monitor_orm.create(monitor_id, generate_monitor_configuration())
        monitor_ids.append(monitor_id)

    result = shinobi_monitor_ansible_task_runner(user=existing_user)
    retrieved_monitors = tuple(filter(lambda monitor: monitor["id"] in monitor_ids, result["monitors"]))
    assert len(retrieved_monitors) == len(monitor_ids)


def test_modify_non_existent_monitor(
        shinobi_monitor_ansible_task_runner, monitor_orm: ShinobiMonitorOrm, does_monitor_exist):
    user = monitor_orm.user
    monitor_id = generate_random_string()
    result = shinobi_monitor_ansible_task_runner(
        monitor_id=monitor_id, configuration=generate_monitor_configuration(), user=user, state="present")
    assert result["changed"]
    assert does_monitor_exist(user, monitor_id)


def test_modify_monitor_with_same_values(shinobi_monitor_ansible_task_runner, existing_user, does_monitor_exist):
    monitor_id = generate_random_string()
    shinobi_monitor_ansible_task_runner(
        id=monitor_id, user=existing_user, configuration=generate_monitor_configuration(1), state="present")
    result = shinobi_monitor_ansible_task_runner(
        id=monitor_id, user=existing_user, configuration=generate_monitor_configuration(1), state="present")
    assert not result["changed"]
    assert does_monitor_exist(existing_user, monitor_id)


def test_modify_monitor_with_different_configuration(
        shinobi_monitor_ansible_task_runner, existing_user, does_monitor_exist):
    monitor_id = generate_random_string()
    result_1 = shinobi_monitor_ansible_task_runner(
        id=monitor_id, user=existing_user, configuration=generate_monitor_configuration(1), state="present")
    result_2 = shinobi_monitor_ansible_task_runner(
        id=monitor_id, user=existing_user, configuration=generate_monitor_configuration(2), state="present")
    assert result_1["monitor"]["details"] != result_2["monitor"]["details"]
    assert does_monitor_exist(existing_user, monitor_id)


def test_delete_non_existent_monitor(shinobi_monitor_ansible_task_runner, existing_user):
    result = shinobi_monitor_ansible_task_runner(id=generate_random_string(), user=existing_user, state="absent")
    assert not result["changed"]


def test_delete_monitor(shinobi_monitor_ansible_task_runner, existing_monitor, does_monitor_exist):
    user = existing_monitor["user"]
    monitor_id = existing_monitor["id"]
    result = shinobi_monitor_ansible_task_runner(user=user, id=existing_monitor["id"], state="absent")
    assert result["changed"]
    assert not does_monitor_exist(user, monitor_id)

