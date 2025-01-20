import json
import uuid
from pathlib import Path

import pytest
from aioresponses import aioresponses
from yarl import URL

from bssclient.client.bssclient import BasicAuthBssClient
from bssclient.client.config import BasicAuthBssConfig, OAuthBssConfig
from bssclient.models.events import EventHeader


@pytest.mark.parametrize(
    "actual_url,expected_tld",
    [
        pytest.param(URL("https://bss.example.com"), URL("https://example.com")),
        pytest.param(URL("https://bss.prod.de"), URL("https://prod.de")),
        pytest.param(URL("https://test.de"), URL("https://test.de")),
        pytest.param(URL("https://localhost"), URL("https://localhost")),
        pytest.param(URL("http://test.localhost"), URL("http://localhost")),
        pytest.param(URL("http://foo.bar.test.localhost"), URL("http://localhost")),
        pytest.param(URL("http://1.2.3.4"), None),
    ],
)
def test_get_tld(actual_url: URL, expected_tld: URL):
    config = BasicAuthBssConfig(server_url=actual_url, usr="user", pwd="password")
    client = BasicAuthBssClient(config)
    actual = client.get_top_level_domain()
    assert actual == expected_tld


def test_oauth_config():
    with pytest.raises(ValueError):
        OAuthBssConfig(server_url=URL("https://bss.example.com"), bearer_token="something-which-is-definittly no token")


async def test_get_events(bss_client_with_basic_auth, caplog) -> None:
    client, bss_config = bss_client_with_basic_auth
    random_guid = uuid.uuid4()
    client.get_events("Prozess", random_guid)
    stats_json_file = Path(__file__).parent / "example_data" / "prozess-events.json"
    with open(stats_json_file, "r", encoding="utf-8") as infile:
        response_body = json.load(infile)
    with aioresponses() as mocked_bss:
        mocked_get_url = f"{bss_config.server_url}api/Event/Prozess/{random_guid}"
        mocked_bss.get(mocked_get_url, status=200, payload=response_body)
        actual = await client.get_events("Prozess", random_guid)
    assert all(isinstance(x, EventHeader) for x in actual)
