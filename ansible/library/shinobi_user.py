#!/usr/bin/python3

# Copyright: (c) 2020, Colin Nolan <cn580@alumni.york.ac.uk>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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

import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

requests_import_error = None
try:
    import requests
except ImportError:
    requests_import_error = traceback.format_exc()

shinobi_client_import_error = None
try:
    from shinobi_client import ShinobiClient, ShinobiWrongPasswordError
except ImportError:
    shinobi_client_import_error = traceback.format_exc()


EMAIL_PARAMETER = "email"
PASSWORD_PARAMETER = "password"
STATE_PARAMETER = "state"
SUPER_USER_TOKEN_PARAMETER = "token"
HOST_PARAMETER = "host"
PORT_PARAMETER = "port"

PRESENT_STATE = "present"
ABSENT_STATE = "absent"


def run_module():
    """
    Run Ansible module.
    """
    module = AnsibleModule(
        argument_spec={
            EMAIL_PARAMETER: dict(type="str"),
            PASSWORD_PARAMETER: dict(type="str", default=None, no_log=True),
            STATE_PARAMETER: dict(type="str", default=None),
            SUPER_USER_TOKEN_PARAMETER: dict(type="str", required=True),
            HOST_PARAMETER: dict(type="str", required=True),
            PORT_PARAMETER: dict(type="int", required=True)
        }
    )
    email = module.params[EMAIL_PARAMETER]
    password = module.params[PASSWORD_PARAMETER]
    state = module.params[STATE_PARAMETER]
    super_user_token = module.params[SUPER_USER_TOKEN_PARAMETER]
    host = module.params[HOST_PARAMETER]
    port = module.params[PORT_PARAMETER]

    if requests_import_error is not None:
        module.fail_json(msg=missing_required_lib("requests"), exception=requests_import_error)
    if shinobi_client_import_error is not None:
        module.fail_json(msg=missing_required_lib("shinobi-client"), exception=shinobi_client_import_error)

    shinobi_client = ShinobiClient(host, port, super_user_token)

    changed = False

    if state is None:
        if password is not None:
            module.fail_json(msg=f"\"password\" must not be supplied if {STATE_PARAMETER} is not set")

        if email is not None:
            info = dict(user=shinobi_client.user.get(email))
        else:
            info = dict(users=shinobi_client.user.get_all())
    else:
        if password is None and state == PRESENT_STATE:
            module.fail_json(msg=f"\"password\" must be supplied if {STATE_PARAMETER} is {PRESENT_STATE}")
        changed, info = modify_user(email, password, state, shinobi_client)

    module.exit_json(changed=changed, **info)


def modify_user(email: str, password: str, state: str, shinobi_client: "ShinobiClient"):
    """
    TODO
    :param email:
    :param password:
    :param state:
    :param shinobi_client:
    :return:
    """
    user = shinobi_client.user.get(email)

    if user:
        if state == ABSENT_STATE:
            deleted = shinobi_client.user.delete(email)
            return deleted, {}
        else:
            try:
                shinobi_client.api_key.get(email, password)
                return False, user
            except ShinobiWrongPasswordError:
                shinobi_client.user.modify(email=email, password=password)
                return True, user

    elif state == PRESENT_STATE:
        user = shinobi_client.user.create(email, password)
        return True, dict(user=user)


if __name__ == "__main__":
    run_module()
