"""contains the actual client"""

import asyncio
import logging
import uuid
from typing import Awaitable, Optional

from aiohttp import BasicAuth, ClientSession, ClientTimeout
from more_itertools import chunked

from bssclient.client.config import BssConfig
from bssclient.models.aufgabe import AufgabeStats
from bssclient.models.ermittlungsauftrag import Ermittlungsauftrag, _ListOfErmittlungsauftraege

_logger = logging.getLogger(__name__)


class BssClient:
    """
    an async wrapper around the BSS API
    """

    def __init__(self, config: BssConfig):
        self._config = config
        self._auth = BasicAuth(login=self._config.usr, password=self._config.pwd)
        self._session_lock = asyncio.Lock()
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        """
        returns a client session (that may be reused or newly created)
        re-using the same (threadsafe) session will be faster than re-creating a new session for every request.
        see https://docs.aiohttp.org/en/stable/http_request_lifecycle.html#how-to-use-the-clientsession
        """
        async with self._session_lock:
            if self._session is None or self._session.closed:
                _logger.info("creating new session")
                self._session = ClientSession(
                    auth=self._auth,
                    timeout=ClientTimeout(60),
                    raise_for_status=True,
                )
            else:
                _logger.log(5, "reusing aiohttp session")  # log level 5 is half as "loud" logging.DEBUG
            return self._session

    async def close_session(self):
        """
        closes the client session
        """
        async with self._session_lock:
            if self._session is not None and not self._session.closed:
                _logger.info("Closing aiohttp session")
                await self._session.close()
                self._session = None

    async def get_ermittlungsauftraege(self, limit: int = 0, offset: int = 0) -> list[Ermittlungsauftrag]:
        """
        get all ermittlungsauftrage in the specified range
        """
        session = await self._get_session()
        request_url = (
            self._config.server_url
            / "api"
            / "Aufgabe"
            / "ermittlungsauftraege"
            % {"limit": limit, "offset": offset, "includeDetails": "true"}
        )
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            response.raise_for_status()  # endpoint returns an empty list but no 404
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            _list_of_ermittlungsauftraege = _ListOfErmittlungsauftraege.model_validate(response_json)
        _logger.debug(
            "Downloaded %i Ermittlungsauftraege (limit %i, offset %i)",
            len(_list_of_ermittlungsauftraege.root),
            limit,
            offset,
        )
        return _list_of_ermittlungsauftraege.root

    async def get_aufgabe_stats(self) -> AufgabeStats:
        """
        get statistics for all aufgaben types
        """
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Aufgabe" / "stats"
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            response.raise_for_status()  # endpoint returns an empty list but no 404
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
        result = AufgabeStats.model_validate(response_json)
        return result

    async def get_all_ermittlungsauftraege(self, package_size: int = 100) -> list[Ermittlungsauftrag]:
        """
        downloads all ermittlungsauftrage in batches of 100
        """
        if package_size < 1:
            raise ValueError("package_size must be at least 1 but was %i" % package_size)
        stats = await self.get_aufgabe_stats()
        total_count = stats.get_sum("Ermittlungsauftrag")
        download_tasks: list[Awaitable[list[Ermittlungsauftrag]]] = []
        for offset in range(0, total_count, package_size):
            if offset + package_size > total_count:
                limit = total_count - offset
            else:
                limit = package_size
            batch = self.get_ermittlungsauftraege(limit=limit, offset=offset)
            download_tasks.append(batch)
        result: list[Ermittlungsauftrag] = []
        for download_tasks_chunk in chunked(download_tasks, 10):  # 10 is arbitrary at this point
            _logger.debug("Downloading %i chunks of Ermittlungsautraege", len(download_tasks_chunk))
            list_of_lists_of_io_from_chunk = await asyncio.gather(*download_tasks_chunk)
            result.extend([item for sublist in list_of_lists_of_io_from_chunk for item in sublist])
        _logger.info("Downloaded %i Ermittlungsautraege", len(result))
        return result
