from typing import Dict

import pytest
from shinobi_client import ShinobiClient

from ._common import create_example_email_and_password, SHINOBI_HOST


@pytest.fixture
def shinobi_client(testvars: Dict) -> ShinobiClient:
    """
    TODO
    :param testvars:
    :return:
    """
    return ShinobiClient(SHINOBI_HOST, testvars["shinobi_host_port"], testvars["shinobi_super_user_token"])


@pytest.fixture
def existing_user(testvars: Dict, shinobi_client: ShinobiClient) -> Dict:
    """
    TODO
    :param testvars:
    :param shinobi_client:
    :return:
    """
    email, password = create_example_email_and_password()
    return shinobi_client.user.create(email=email, password=password)
