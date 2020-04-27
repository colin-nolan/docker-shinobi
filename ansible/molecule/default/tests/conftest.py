from typing import Dict

import pytest
from shinobi_client import ShinobiClient, ShinobiMonitorOrm

from ._common import create_example_email_and_password, SHINOBI_HOST, generate_random_string
from .module.resources.metadata import generate_monitor_configuration


@pytest.fixture
def shinobi_client(testvars: Dict) -> ShinobiClient:
    """
    TODO
    :param testvars:
    :return:
    """
    return ShinobiClient(SHINOBI_HOST, testvars["shinobi_host_port"], testvars["shinobi_super_user_token"])


@pytest.fixture
def monitor_orm(shinobi_client, existing_user) -> ShinobiMonitorOrm:
    """
    TODO
    :return:
    """
    return shinobi_client.monitor(existing_user["email"], existing_user["password"])


@pytest.fixture
def existing_user(shinobi_client: ShinobiClient) -> Dict:
    """
    TODO
    :param shinobi_client:
    :return:
    """
    email, password = create_example_email_and_password()
    return shinobi_client.user.create(email=email, password=password)


@pytest.fixture
def existing_monitor(monitor_orm: ShinobiMonitorOrm) -> Dict:
    """
    TODO
    :param monitor_orm:
    :return:
    """
    monitor_id = generate_random_string()
    monitor = monitor_orm.create(monitor_id, generate_monitor_configuration())
    assert "user" not in monitor
    monitor["user"] = monitor_orm.user
    return monitor
