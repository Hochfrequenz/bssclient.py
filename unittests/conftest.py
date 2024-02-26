from typing import AsyncGenerator

import pytest
from yarl import URL

from tmdsclient import TmdsClient, TmdsConfig


@pytest.fixture
async def tmds_client_with_default_auth() -> AsyncGenerator[tuple[TmdsClient, TmdsConfig], None]:
    """
    "mention" this fixture in the signature of your test to run the code up to yield before the respective test
    (and the code after yield the test execution)
    :return:
    """
    tmds_config = TmdsConfig(
        server_url=URL("https://tmds.inv/"),
        usr="my-usr",
        pwd="my-pwd",
    )
    client = TmdsClient(tmds_config)
    yield client, tmds_config
    await client.close_session()
