from typing import AsyncGenerator

import pytest
from pydantic import HttpUrl
from pydantic_core import Url
from yarl import URL

from bssclient import BssClient, BssConfig
from bssclient.client.bssclient import BasicAuthBssClient, OAuthBssClient
from bssclient.client.config import BasicAuthBssConfig, OAuthBssConfig


@pytest.fixture
async def bss_client_with_basic_auth() -> AsyncGenerator[tuple[BssClient, BssConfig], None]:
    """
    "mention" this fixture in the signature of your test to run the code up to yield before the respective test
    (and the code after yield the test execution)
    :return:
    """
    bss_config = BasicAuthBssConfig(
        server_url=URL("https://bss.inv/"),
        usr="my-usr",
        pwd="my-pwd",
    )
    client = BasicAuthBssClient(bss_config)
    yield client, bss_config
    await client.close_session()


@pytest.fixture
async def bss_client_with_oauth() -> AsyncGenerator[tuple[BssClient, BssConfig], None]:
    """
    "mention" this fixture in the signature of your test to run the code up to yield before the respective test
    (and the code after yield the test execution)
    :return:
    """
    bss_config = OAuthBssConfig(
        server_url=URL("https://basicsupply.invalid.de/"),
        client_id="my-client-id",
        client_secret="my-client-secret",
        token_url=HttpUrl("https://validate-my-token.inv"),
    )
    client = OAuthBssClient(bss_config)
    yield client, bss_config
    await client.close_session()
