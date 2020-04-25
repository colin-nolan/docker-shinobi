#!/usr/bin/python3

import traceback
from typing import Tuple, Optional, Dict

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

shinobi_client_import_error = None
try:
    from shinobi_client import ShinobiClient, ShinobiWrongPasswordError
except ImportError:
    shinobi_client_import_error = traceback.format_exc()

HOST_PARAMETER = "host"
PORT_PARAMETER = "port"
SUPER_USER_TOKEN_PARAMETER = "token"
STATE_PARAMETER = "state"
EMAIL_PARAMETER = "email"
PASSWORD_PARAMETER = "password"

PRESENT_STATE = "present"
ABSENT_STATE = "absent"


def run_module():
    module = AnsibleModule(
        argument_spec={
            HOST_PARAMETER: dict(type="str", required=True),
            PORT_PARAMETER: dict(type="int", required=True),
            SUPER_USER_TOKEN_PARAMETER: dict(type="str", required=True),
            STATE_PARAMETER: dict(type="str", default=None),
            EMAIL_PARAMETER: dict(type="str"),
            PASSWORD_PARAMETER: dict(type="str", default=None, no_log=True)
        }
    )
    host = module.params[HOST_PARAMETER]
    port = module.params[PORT_PARAMETER]
    super_user_token = module.params[SUPER_USER_TOKEN_PARAMETER]
    state = module.params[STATE_PARAMETER]
    email = module.params[EMAIL_PARAMETER]
    password = module.params[PASSWORD_PARAMETER]

    if shinobi_client_import_error is not None:
        module.fail_json(msg=missing_required_lib("shinobi-client"), exception=shinobi_client_import_error)

    shinobi_client = ShinobiClient(host, port, super_user_token)

    changed = False

    if state is None:
        if password is not None:
            module.fail_json(msg=f"\"{PASSWORD_PARAMETER}\" must not be supplied if {STATE_PARAMETER} is not set")

        if email is not None:
            info = dict(user=shinobi_client.user.get(email))
        else:
            info = dict(users=shinobi_client.user.get_all())
    else:
        if password is None and state == PRESENT_STATE:
            module.fail_json(msg=f"\"password\" must be supplied if {STATE_PARAMETER} is {PRESENT_STATE}")
        changed, info = modify_user(email, state, shinobi_client, password=password)

    if info is None:
        module.exit_json(changed=changed)
    else:
        module.exit_json(changed=changed, **info)


def modify_user(email: str, state: str, shinobi_client: ShinobiClient, *, password: str) -> Tuple[bool, Optional[Dict]]:
    user = shinobi_client.user.get(email)

    if user:
        if state == ABSENT_STATE:
            deleted = shinobi_client.user.delete(email)
            return deleted, None
        else:
            try:
                shinobi_client.api_key.get(email, password)
                return False, user
            except ShinobiWrongPasswordError:
                shinobi_client.user.modify(email=email, password=password)
                return True, user
    else:
        if state == PRESENT_STATE:
            user = shinobi_client.user.create(email, password)
            return True, dict(user=user)
        else:
            return False, None


if __name__ == "__main__":
    run_module()
