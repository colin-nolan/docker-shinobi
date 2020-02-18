import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_containers_running(host):
    containers = host.docker.get_containers(name="shinobi")
    assert len(containers) == 2


def test_shinobi_ui_available(host):
    shinobi = host.addr("0.0.0.0")
    # FIXME: hardcoded 8080
    assert shinobi.port(8080).is_reachable


# def test_shinobi_login(host):
#     command = host.run("curl http://localhost:8080")
#     raise Exception(command)
