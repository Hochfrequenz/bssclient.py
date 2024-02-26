from typing import AsyncGenerator

import pytest
from yarl import URL

from bssclient import BssClient, BssConfig


@pytest.fixture
async def bss_client_with_default_auth() -> AsyncGenerator[tuple[BssClient, BssConfig], None]:
    """
    "mention" this fixture in the signature of your test to run the code up to yield before the respective test
    (and the code after yield the test execution)
    :return:
    """
    tmds_config = BssConfig(
        server_url=URL("https://bss.inv/"),
        usr="my-usr",
        pwd="my-pwd",
    )
    client = BssClient(tmds_config)
    yield client, tmds_config
    await client.close_session()
