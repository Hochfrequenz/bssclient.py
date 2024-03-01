import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from aioresponses import aioresponses

from bssclient.models.aufgabe import AufgabeStats
from bssclient.models.ermittlungsauftrag import Ermittlungsauftrag


class TestErmittlungsauftraege:
    """
    A class with pytest unit tests.
    """

    async def test_get_ermittlungsauftraege(self, bss_client_with_default_auth):
        ermittlungsauftraege_json_file = Path(__file__).parent / "example_data" / "list_of_1_ermittlungsauftraege.json"
        ermittlungsauftraege_json_file2 = (
            Path(__file__).parent / "example_data" / "list_of_1_ermittlungsauftrag_from_topcom.json"
        )
        with (
            open(ermittlungsauftraege_json_file, "r", encoding="utf-8") as infile1,
            open(ermittlungsauftraege_json_file2, "r", encoding="utf-8") as infile2,
        ):
            ermittlungsauftraege = json.load(infile1) + json.load(infile2)
        client, bss_config = bss_client_with_default_auth
        with aioresponses() as mocked_bss:
            mocked_get_url = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=2&offset=0"
            )
            mocked_bss.get(mocked_get_url, status=200, payload=ermittlungsauftraege)
            actual = await client.get_ermittlungsauftraege(limit=2)
        assert isinstance(actual, list)
        assert len(actual) == 2
        assert all(isinstance(x, Ermittlungsauftrag) for x in actual)
        assert isinstance(actual[0].prozess.deserialized_ausloeser, dict)
        assert actual[0].get_vertragsbeginn_from_boneycomb_or_topcom() == datetime(
            2023, 10, 31, 23, 0, 0, tzinfo=timezone.utc
        )
        assert actual[1].get_vertragsbeginn_from_boneycomb_or_topcom() == datetime(
            2020, 4, 17, 22, 0, tzinfo=timezone.utc
        )

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
        assert actual.get_sum("Ermittlungsauftrag") == 11518

    async def test_get_all_ermittlungsauftraege(self, bss_client_with_default_auth):
        ermittlungsauftraege_json_file = Path(__file__).parent / "example_data" / "list_of_1_ermittlungsauftraege.json"
        with open(ermittlungsauftraege_json_file, "r", encoding="utf-8") as infile:
            ermittlungsauftraege = json.load(infile)
        client, bss_config = bss_client_with_default_auth
        stats_mock = Mock(AufgabeStats)

        def return_345(t):
            assert t == "Ermittlungsauftrag"
            return 345

        stats_mock.get_sum = return_345
        client.get_aufgabe_stats = AsyncMock()
        client.get_aufgabe_stats.return_value = stats_mock
        with aioresponses() as mocked_bss:
            mocked_get_url0 = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=100&offset=0"
            )
            mocked_get_url1 = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=100&offset=100"
            )
            mocked_get_url2 = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=100&offset=200"
            )
            mocked_get_url3 = (
                f"{bss_config.server_url}api/Aufgabe/ermittlungsauftraege?includeDetails=true&limit=45&offset=300"
            )
            mocked_bss.get(mocked_get_url0, status=200, payload=100 * ermittlungsauftraege)
            mocked_bss.get(mocked_get_url1, status=200, payload=100 * ermittlungsauftraege)
            mocked_bss.get(mocked_get_url2, status=200, payload=100 * ermittlungsauftraege)
            mocked_bss.get(mocked_get_url3, status=200, payload=45 * ermittlungsauftraege)
            actual = await client.get_all_ermittlungsauftraege()
        assert isinstance(actual, list)
        assert len(actual) == 345
        assert all(isinstance(x, Ermittlungsauftrag) for x in actual)
