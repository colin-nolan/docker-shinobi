#!/usr/bin/python3

# TODO: Docs
DOCUMENTATION = '''
---
module: 

short_description: 

description:
  - 
    
  - Note:

options:
    enabled:
        description:
            - Whether HDMI should be enabled
        required: true

author:
    - Colin Nolan (@colin-nolan)
'''

EXAMPLES = '''
- name: set HDMI
  rpi_hdmi:
    enabled: "{{ hdmi_enabled }}"
  when: host_is_rpi 
'''

from typing import Dict, Tuple, Optional
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

shinobi_client_import_error = None
try:
    from shinobi_client import ShinobiClient, ShinobiWrongPasswordError, ShinobiMonitorOrm
except ImportError:
    shinobi_client_import_error = traceback.format_exc()

HOST_PARAMETER = "host"
PORT_PARAMETER = "port"
STATE_PARAMETER = "state"
EMAIL_PARAMETER = "email"
PASSWORD_PARAMETER = "password"
MONITOR_ID_PARAMETER = "id"
CONFIGURATION_PARAMETER = "configuration"

PRESENT_STATE = "present"
ABSENT_STATE = "absent"


def run_module():
    module = AnsibleModule(
        argument_spec={
            HOST_PARAMETER: dict(type="str", required=True),
            PORT_PARAMETER: dict(type="int", required=True),
            STATE_PARAMETER: dict(type="str", default=None),
            EMAIL_PARAMETER: dict(type="str", required=True),
            PASSWORD_PARAMETER: dict(type="str", required=True, no_log=True),
            MONITOR_ID_PARAMETER: dict(type="str"),
            CONFIGURATION_PARAMETER: dict(type="dict")
        }
    )
    host = module.params[HOST_PARAMETER]
    port = module.params[PORT_PARAMETER]
    state = module.params[STATE_PARAMETER]
    email = module.params[EMAIL_PARAMETER]
    password = module.params[PASSWORD_PARAMETER]
    monitor_id = module.params[MONITOR_ID_PARAMETER]
    configuration = module.params[CONFIGURATION_PARAMETER]

    if shinobi_client_import_error is not None:
        module.fail_json(msg=missing_required_lib("shinobi-client"), exception=shinobi_client_import_error)
    if email is None:
        module.fail_json(msg="The email of the user to set the monitor for must be given")
    if password is None:
        module.fail_json(msg="The password of the user to set the monitor for must be given")
    if monitor_id is None:
        module.fail_json(msg="The ID of the monitor to be set must be given")

    try:
        shinobi_monitor_orm = ShinobiClient(host, port).monitor(email, password)
    except ShinobiWrongPasswordError:
        module.fail_json(msg=f"Invalid email address and password pair")
        return

    changed = False

    if state is None:
        if configuration is not None:
            module.fail_json(msg=f"\"{CONFIGURATION_PARAMETER}\" must not be supplied if {STATE_PARAMETER} is not set")

        if monitor_id is not None:
            info = dict(user=shinobi_monitor_orm.get(monitor_id))
        else:
            info = dict(users=shinobi_monitor_orm.get_all())
    else:
        if configuration is None:
            module.fail_json(msg=f"\"{CONFIGURATION_PARAMETER}\" must be supplied to setup a monitor")
        changed, info = modify_monitor(shinobi_monitor_orm, state, monitor_id, configuration)

    if info is None:
        module.exit_json(changed=changed)
    else:
        module.exit_json(changed=changed, **info)


def modify_monitor(shinobi_monitor_orm: ShinobiMonitorOrm, state: str, monitor_id: str, configuration: Dict = None) \
        -> Tuple[bool, Optional[Dict]]:
    monitor = shinobi_monitor_orm.get(monitor_id)

    if monitor:
        if state == ABSENT_STATE:
            deleted = shinobi_monitor_orm.delete(monitor_id)
            return deleted, None
        else:
            modified = shinobi_monitor_orm.modify(monitor_id, configuration)
            return modified, configuration
    else:
        if state == PRESENT_STATE:
            monitor = shinobi_monitor_orm.create(monitor_id, configuration)
            return True, monitor
        else:
            return False, None


if __name__ == "__main__":
    run_module()
