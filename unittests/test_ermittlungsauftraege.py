import json
from pathlib import Path

from aioresponses import aioresponses

from bssclient.models.aufgabe import AufgabeStats
from bssclient.models.ermittlungsauftrag import Ermittlungsauftrag


class TestErmittlungsauftraege:
    """
    A class with pytest unit tests.
    """

    async def test_get_ermittlungsauftraege(self, bss_client_with_default_auth):
        ermittlungsauftraege_json_file = Path(__file__).parent / "example_data" / "list_of_1_ermittlungsauftraege.json"
        with open(ermittlungsauftraege_json_file, "r", encoding="utf-8") as infile:
            ermittlungsauftraege = json.load(infile)
        client, bss_config = bss_client_with_default_auth
        with aioresponses() as mocked_bss:
            mocked_get_url = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=1&offset=0"
            )
            mocked_bss.get(mocked_get_url, status=200, payload=ermittlungsauftraege)
            actual = await client.get_ermittlungsauftraege(limit=1)
        assert isinstance(actual, list)
        assert all(isinstance(x, Ermittlungsauftrag) for x in actual)

    async def test_get_stats(self, bss_client_with_default_auth):
        stats_json_file = Path(__file__).parent / "example_data" / "aufgabe_stats.json"
        with open(stats_json_file, "r", encoding="utf-8") as infile:
            stats = json.load(infile)
        client, bss_config = bss_client_with_default_auth
        with aioresponses() as mocked_bss:
            mocked_get_url = f"{bss_config.server_url}api/Aufgabe/stats"
            mocked_bss.get(mocked_get_url, status=200, payload=stats)
            actual = await client.get_aufgabe_stats()
        assert isinstance(actual, AufgabeStats)
        assert actual.stats["Ermittlungsauftrag"]["status"]["Beendet"] == 2692
