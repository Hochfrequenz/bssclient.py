import pytest
from yarl import URL

from bssclient import BssClient, BssConfig


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
    config = BssConfig(server_url=actual_url, usr="user", pwd="password")
    client = BssClient(config)
    actual = client.get_top_level_domain()
    assert actual == expected_tld
