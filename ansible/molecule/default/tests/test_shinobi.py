import os
import json

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_containers_running(host):
    containers = host.docker.get_containers(name="shinobi")
    assert len(containers) == 2


def test_shinobi_ui_available(host):
    shinobi = host.addr("0.0.0.0")
    assert shinobi.port(8080).is_reachable


def test_shinobi_super_user(host):
    input_data = {
        "mail": "admin@localhost",
        "pass": "password123",
        "function": "dash",
        "machineID": "fMUVxYdG1X3hWb7GNkTd"
    }
    output = host.run(
        f"curl -s -H 'Content-Type: application/json' -d '{json.dumps(input_data)}' "
        f"http://localhost:8080/super/token123/accounts/list")
    assert output.exit_status == 0

    parsed_stdout = json.loads(output.stdout)
    assert parsed_stdout["ok"]
