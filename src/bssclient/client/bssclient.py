"""contains the actual client"""

import asyncio
import logging
import uuid
from typing import Optional

from aiohttp import BasicAuth, ClientSession, ClientTimeout

from bssclient.client.config import BssConfig
from bssclient.models.netzvertrag import Netzvertrag, _ListOfNetzvertraege

_logger = logging.getLogger(__name__)


class BssClient:
    """
    an async wrapper around the TMDS API
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

    async def get_netzvertraege_for_melo(self, melo_id: str) -> list[Netzvertrag]:
        """
        provide a melo id, e.g. 'DE1234567890123456789012345678901' and get the corresponding netzvertrag
        """
        if not melo_id:
            raise ValueError("You must not provide an empty melo_id")
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Netzvertrag" / "find" % {"messlokation": melo_id}
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            response.raise_for_status()  # endpoint returns an empty list but no 404
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            _list_of_netzvertraege = _ListOfNetzvertraege.model_validate(response_json)
        return _list_of_netzvertraege.root

    async def get_netzvertrag_by_id(self, nv_id: uuid.UUID) -> Netzvertrag | None:
        """
        provide a UUID, get the matching netzvertrag in return (or None, if 404)
        """
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Netzvertrag" / str(nv_id)
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            try:
                if response.status == 404:
                    return None
                response.raise_for_status()
            finally:
                _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            result = Netzvertrag.model_validate(response_json)
        return result
