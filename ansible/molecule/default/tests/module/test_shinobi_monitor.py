import json
from typing import Dict, Callable

import pytest
import takeltest
from shinobi_client import ShinobiClient, ShinobiMonitorOrm
from testinfra.host import Host

from .resources.metadata import get_monitor_configuration
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


def test_create_monitor(shinobi_monitor_ansible_task_runner, existing_user, shinobi_client: ShinobiClient):
    email = existing_user["email"]
    password = existing_user["password"]
    monitor_id = generate_random_string()
    configuration = get_monitor_configuration()

    parameter_arguments = dict(
        email=email, password=password, state="present", id=monitor_id, configuration=configuration)

    result = shinobi_monitor_ansible_task_runner(**parameter_arguments)
    assert result["changed"]
    assert "id" in result

    shinobi_monitor_orm = shinobi_client.monitor(email, password)
    monitor = shinobi_monitor_orm.get(result["id"])
    assert monitor is not None
    assert ShinobiMonitorOrm.is_configuration_equivalent(configuration, monitor)

    # Testing idempotence
    result = shinobi_monitor_ansible_task_runner(**parameter_arguments)
    monitor = shinobi_monitor_orm.get(result["id"])
    assert monitor is not None
    assert ShinobiMonitorOrm.is_configuration_equivalent(configuration, monitor)


def test_delete_non_existent_monitor(shinobi_monitor_ansible_task_runner):
    email, _ = create_example_email_and_password()
    result = shinobi_monitor_ansible_task_runner(email=email, state="absent")
    assert not result["changed"]
