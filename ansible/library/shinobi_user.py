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

import json
from requests import Response
import traceback
from typing import List, Dict, Optional
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

requestsImportError = None
try:
    import requests
except ImportError:
    requestsImportError = traceback.format_exc()


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
        },
        # We cannot support checked mode as changing as user's password
        supports_check_mode=False
    )
    email = module.params[EMAIL_PARAMETER]
    password = module.params[PASSWORD_PARAMETER]
    state = module.params[STATE_PARAMETER]
    super_user_token = module.params[SUPER_USER_TOKEN_PARAMETER]
    host = module.params[HOST_PARAMETER]
    port = module.params[PORT_PARAMETER]

    if requestsImportError is not None:
        module.fail_json(msg=missing_required_lib("requests"), exception=requestsImportError)

    user_orm = ShinobiUserOrm(host, port, super_user_token)

    changed = False

    if state is None:
        if password is not None:
            module.fail_json(msg=f"\"password\" must not be supplied if {STATE_PARAMETER} is not set")

        if email is not None:
            info = dict(user=user_orm.get(email))
        else:
            info = dict(users=user_orm.get_all())
    else:
        if password is None and state == PRESENT_STATE:
            module.fail_json(msg=f"\"password\" must be supplied if {STATE_PARAMETER} is {PRESENT_STATE}")
        changed, info = modify_user(email, password, state, user_orm)

    module.exit_json(changed=changed, **info)


# TODO: if move ShinobiUserOrm then quotes not needed here
def modify_user(email: str, password: str, state: str, user_orm: "ShinobiUserOrm"):
    """
    TODO
    :param email:
    :param password:
    :param state:
    :param user_orm:
    :return:
    """
    user = user_orm.get(email)

    if user:
        if state == ABSENT_STATE:
            deleted = user_orm.delete(email)
            return deleted, {}
        else:
            # Unfortunately there is no way to dry-run a modification, hence we lose check_mode support
            updated_user = {
                "mail": email,
                "pass": password
            }
            changed = user_orm.modify(updated_user)
            return changed, {}
    elif state == PRESENT_STATE:
        user = user_orm.create(email, password)
        return True, dict(user=user)


class ShinobiUserOrm:
    """
    TODO
    """
    SUPPORTED_MODIFIABLE_PROPERTIES = {"pass"}

    def __init__(self, host: str, port: int, super_user_token: str):
        """
        TODO
        :param host:
        :param port:
        :param super_user_token:
        """
        self.host = host
        self.port = port
        self.super_user_token = super_user_token

    def get_all(self) -> List:
        """
        TODO
        :return:
        """
        response = requests.get(
            f"http://{self.host}:{self.port}/super/{self.super_user_token}/accounts/list")
        self._raise_if_errors(response)
        return response.json()["users"]

    def get(self, email: str) -> Optional[Dict]:
        """
        TODO
        :param email:
        :return:
        """
        # For some reason, Shinobi doesn't have an endpoint to query an individual user
        users = self.get_all()
        matched_users = tuple(filter(lambda user: user["mail"] == email, users))
        assert len(matched_users) <= 1, f"More than one user found with the email address: {email}"
        if len(matched_users) == 1:
            return matched_users[0]
        else:
            return None

    def create(self, email: str, password: str, verify_create: bool=True) -> Dict:
        """
        TODO
        :param email:
        :param password:
        :param verify_create:
        :return:
        """
        # Not trusting Shinobi's API to give back anything useful if the user already exists
        if self.get(email):
            raise ValueError(f"User with email \"{email}\" already exists")

        # The required post does not align with the API documentation (https://shinobi.video/docs/api)
        # Exploiting the undocumented API successfully used by UI.
        # See source: https://gitlab.com/Shinobi-Systems/Shinobi/-/blob/dev/libs/webServerSuperPaths.js
        data = {
            "mail": email,
            "pass": password,
            "password_again": password,
            "details": json.dumps({
                "factorAuth": "0", "size": "", "days": "", "event_days": "", "log_days": "", "max_camera": "",
                "permissions": "all", "edit_size": "1", "edit_days": "1", "edit_event_days": "1",
                "edit_log_days": "1", "use_admin": "1", "use_aws_s3": "1", "use_whcs": "1", "use_sftp": "1",
                "use_webdav": "1", "use_discordbot": "1", "use_ldap": "1", "aws_use_global": "0",
                "b2_use_global": "0", "webdav_use_global": "0"})
        }
        response = requests.post(
            f"http://{self.host}:{self.port}/super/{self.super_user_token}/accounts/registerAdmin",
            json=dict(data=data))
        self._raise_if_errors(response)
        create_user = response.json()

        # This is worth doing as Shinobi's API is all over the place - it happily returns OK for invalid requests
        if verify_create:
            assert self.get(email), "Unable to get created user"

        return create_user["user"]

    def modify(self, user: Dict) -> bool:
        """
        TODO
        :param user:
        :return:
        """
        if "mail" not in user:
            raise ValueError("User must have \"mail\" property")

        unsupported_properties = set(user.keys()) - {"mail"} - self.__class__.SUPPORTED_MODIFIABLE_PROPERTIES
        if len(unsupported_properties) > 0:
            raise NotImplementedError(f"Cannot modify user properties: {unsupported_properties}")

        existing_user = self.get(user["mail"])
        if existing_user is None:
            raise ValueError(f"Cannot modify user as they do not exist: {user['mail']}")

        data = {
            "mail": user["mail"],
            "pass": user["pass"],
            "password_again": user["pass"],
        }
        account = {
            "mail": user["mail"],
            "uid": existing_user["uid"],
            "ke": existing_user["ke"]
        }
        response = requests.post(
            f"http://{self.host}:{self.port}/super/{self.super_user_token}/accounts/editAdmin",
            json=dict(data=data, account=account))
        self._raise_if_errors(response)

        return response.json()["rowsChanged"] == 1

    def delete(self, email: str, verify_delete: bool=True) -> bool:
        """
        TODO
        :param email:
        :param verify_delete:
        :return:
        """
        user = self.get(email)
        if user is None:
            return False

        account = {
            "uid": user["uid"],
            "ke": user["ke"],
            "mail": email
        }

        # Odd interface, defined here:
        # https://gitlab.com/Shinobi-Systems/Shinobi/-/blob/dev/libs/webServerSuperPaths.js#L385
        response = requests.post(
            f"http://{self.host}:{self.port}/super/{self.super_user_token}/accounts/deleteAdmin",
            json=dict(account=account))
        self._raise_if_errors(response)

        if verify_delete:
            assert self.get(email) is None, f"User with email \"{email}\" was not deleted"

        return True

    def _raise_if_errors(self, shinobi_response: Response):
        """
        TODO
        :param shinobi_response:
        :return:
        """
        shinobi_response.raise_for_status()
        json_response = shinobi_response.json()
        if not json_response["ok"]:
            # Yes, the API returns a non-400 when everything is not ok...
            raise RuntimeError(json_response["msg"])


if __name__ == "__main__":
    run_module()
