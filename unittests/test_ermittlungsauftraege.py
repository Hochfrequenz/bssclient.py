import json
from pathlib import Path

from aioresponses import aioresponses

from bssclient.models.ermittlungsauftrag import Ermittlungsauftrag


class TestGetErmittlungsauftraege:
    """
    A class with pytest unit tests.
    """

    async def test_get_ermittlungsauftraege(self, bss_client_with_default_auth):
        ermittlungsauftraege_json_file = Path(__file__).parent / "example_data" / "list_of_1_ermittlungsauftraege.json"
        with open(ermittlungsauftraege_json_file, "r", encoding="utf-8") as infile:
            ermittlungsauftraege = json.load(infile)
        client, bss_config = bss_client_with_default_auth
        with aioresponses() as mocked_tmds:
            mocked_get_url = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=1&offset=0"
            )
            mocked_tmds.get(mocked_get_url, status=200, payload=ermittlungsauftraege)
            actual = await client.get_ermittlungsauftraege(limit=1)
        assert isinstance(actual, list)
        assert all(isinstance(x, Ermittlungsauftrag) for x in actual)
