from typing import Dict

import testaid
from shinobi_client import ShinobiClient
from testinfra.host import Host

from .._common import create_example_email_and_password

testinfra_hosts = testaid.hosts()


def test_containers_running(host: Host):
    containers = host.docker.get_containers(name="shinobi")
    assert len(containers) == 2


def test_shinobi_ui_available(host: Host, testvars: Dict):
    shinobi = host.addr("0.0.0.0")
    assert shinobi.port(testvars["shinobi_host_port"]).is_reachable


def test_shinobi_super_user(host: Host, testvars: Dict):
    shinobi_client = ShinobiClient("0.0.0.0", testvars["shinobi_host_port"], testvars["shinobi_super_user_token"])
    email, password = create_example_email_and_password()
    shinobi_client.user.create(email, password)
    assert shinobi_client.user.get(email) is not None
