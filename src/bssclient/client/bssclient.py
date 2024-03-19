"""contains the actual client"""

import asyncio
import logging
import uuid
from abc import ABC
from typing import Awaitable, Optional

from aiohttp import BasicAuth, ClientSession, ClientTimeout
from more_itertools import chunked
from yarl import URL

from bssclient.client.config import BasicAuthBssConfig, BssConfig, OAuthBssConfig
from bssclient.client.oauth import _OAuthHttpClient
from bssclient.models.aufgabe import AufgabeStats
from bssclient.models.ermittlungsauftrag import Ermittlungsauftrag, _ListOfErmittlungsauftraege

_logger = logging.getLogger(__name__)


class BssClient(ABC):
    """
    an async wrapper around the BSS API
    """

    def __init__(self, config: BssConfig):
        self._config = config
        self._session_lock = asyncio.Lock()
        self._session: Optional[ClientSession] = None
        _logger.info("Instantiated BssClient with server_url %s", str(self._config.server_url))

    async def _get_session(self):
        raise NotImplementedError("The inheriting class has to implement this with its respective authentication")

    def get_top_level_domain(self) -> URL | None:
        """
        Returns the top level domain of the server_url; this is useful to differentiate prod from test systems.
        If the server_url is an IP address, None is returned.
        """
        # this method is unit tested; check the testcases to understand its branches
        domain_parts = self._config.server_url.host.split(".")  # type:ignore[union-attr]
        if all(x.isnumeric() for x in domain_parts):
            # seems like this is an IP address
            return None
        if not any(domain_parts):
            return self._config.server_url
        tld: str
        if domain_parts[-1] == "localhost":
            tld = ".".join(domain_parts[-1:])
        else:
            tld = ".".join(domain_parts[-2:])
        return URL(self._config.server_url.scheme + "://" + tld)

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

    async def get_ermittlungsauftraege_by_malo(self, malo_id: str) -> list[Ermittlungsauftrag]:
        """
        find ermittlungsauftraege by their marktlokations-id
        """
        if malo_id is None or not isinstance(malo_id, str) or not malo_id.strip():
            raise ValueError(f"malo_id must not be empty but was '{malo_id}'")
        session = await self._get_session()
        # see https://basicsupply.xtk-dev.de/swagger/index.html#operations-Aufgabe-get_api_Aufgabe_ermittlungsauftraege
        request_url = (
            self._config.server_url
            / "api"
            / "Aufgabe"
            / "ermittlungsauftraege"
            % {"marktlokationid": malo_id, "includeDetails": "true"}
        )
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            response.raise_for_status()  # endpoint returns an empty list but no 404
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            _list_of_ermittlungsauftraege = _ListOfErmittlungsauftraege.model_validate(response_json)
        _logger.debug(
            "Downloaded %i Ermittlungsauftraege for MaLo '%s'", len(_list_of_ermittlungsauftraege.root), malo_id
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
            raise ValueError(f"package_size must be at least 1 but was {package_size}")
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


class BasicAuthBssClient(BssClient):
    """BSS client with basic auth"""

    def __init__(self, config: BasicAuthBssConfig):
        """instantiate by providing a valid config"""
        if not isinstance(config, BasicAuthBssConfig):
            raise ValueError("You must provide a valid config")
        super().__init__(config)
        self._auth = BasicAuth(login=self._config.usr, password=self._config.pwd)

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


class OAuthBssClient(BssClient, _OAuthHttpClient):
    """BSS client with OAuth"""

    def __init__(self, config: OAuthBssConfig):
        if not isinstance(config, OAuthBssConfig):
            raise ValueError("You must provide a valid config")
        super().__init__(config)
        _OAuthHttpClient.__init__(
            self,
            base_url=config.server_url,
            oauth_client_id=config.client_id,
            oauth_client_secret=config.client_secret,
            oauth_token_url=config.token_url,
        )
        self._oauth_config = config
        self._bearer_token: str | None = None

    async def _get_session(self) -> ClientSession:
        """
        returns a client session (that may be reused or newly created)
        re-using the same (threadsafe) session will be faster than re-creating a new session for every request.
        see https://docs.aiohttp.org/en/stable/http_request_lifecycle.html#how-to-use-the-clientsession
        """
        async with self._session_lock:
            if self._bearer_token is None:
                self._bearer_token = await self._get_oauth_token()
            elif not self._token_is_valid(self._bearer_token):
                await self.close_session()
            if self._session is None or self._session.closed:
                _logger.info("creating new session")
                self._session = ClientSession(
                    timeout=ClientTimeout(60),
                    raise_for_status=True,
                    headers={"Authorization": f"Bearer {self._bearer_token}"},
                )
            else:
                _logger.log(5, "reusing aiohttp session")  # log level 5 is half as "loud" logging.DEBUG
            return self._session
