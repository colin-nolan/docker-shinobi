from typing import Dict

from shinobi_client import ShinobiClient
from testinfra.host import Host

from .._common import create_example_email_and_password, SHINOBI_HOST


def test_containers_running(host: Host):
    containers = host.docker.get_containers(name="shinobi")
    assert len(containers) == 2


def test_shinobi_ui_available(host: Host, testvars: Dict):
    shinobi = host.addr(SHINOBI_HOST)
    assert shinobi.port(testvars["shinobi_host_port"]).is_reachable


def test_shinobi_super_user(testvars: Dict):
    shinobi_client = ShinobiClient(SHINOBI_HOST, testvars["shinobi_host_port"], testvars["shinobi_super_user_token"])
    email, password = create_example_email_and_password()
    shinobi_client.user.create(email, password)
    assert shinobi_client.user.get(email) is not None
