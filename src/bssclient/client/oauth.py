"""
oauth stuff
"""

import asyncio
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Optional

import jwt
from aioauth_client import OAuth2Client
from yarl import URL

_logger = logging.getLogger(__name__)


class _ValidateTokenMixin:  # pylint:disable=too-few-public-methods
    """
    Mixin for classes which need to validate tokens
    """

    def __init__(self):
        self._session_lock = asyncio.Lock()

    def _token_is_valid(self, token) -> bool:
        """
        returns true iff the token expiration date is far enough in the future. By "enough" I mean:
        more than 1 minute (because the clients' request using the token shouldn't take longer than that)
        """
        try:
            decoded_token = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
            expiration_timestamp = decoded_token.get("exp")
            expiration_datetime = datetime.fromtimestamp(expiration_timestamp)
            _logger.debug("Token is valid until %s", expiration_datetime.isoformat())
            current_datetime = datetime.utcnow()
            token_is_valid_one_minute_into_the_future = expiration_datetime > current_datetime + timedelta(minutes=1)
            return token_is_valid_one_minute_into_the_future
        except jwt.ExpiredSignatureError:
            _logger.info("The token is expired", exc_info=True)
            return False
        except jwt.InvalidTokenError:
            _logger.info("The token is invalid", exc_info=True)
            return False


class _OAuthHttpClient(_ValidateTokenMixin, ABC):  # pylint:disable=too-few-public-methods
    """
    An abstract oauth based HTTP client
    """

    def __init__(self, base_url: URL, oauth_client_id: str, oauth_client_secret: str, oauth_token_url: URL | str):
        """
        instantiate by providing the basic information which is required to connect to the service.
        :param base_url: e.g. "https://transformerbee.utilibee.io/"
        :param oauth_client_id: e.g. "my-client-id"
        :param oauth_client_secret: e.g. "my-client-secret"
        :param oauth_token_url: e.g."https://transformerbee.utilibee.io/oauth/token"
        """
        super().__init__()
        if not isinstance(base_url, URL):
            # For the cases where type-check is not enough because we tend to ignore type-check warnings
            raise ValueError(f"Pass the base URL as yarl URL or bad things will happen. Got {base_url.__class__}")
        self._base_url = base_url
        self._oauth2client = OAuth2Client(
            client_id=oauth_client_id,
            client_secret=oauth_client_secret,
            access_token_url=str(oauth_token_url),
            logger=_logger,
        )
        self._token: Optional[str] = None  # the jwt token if we did an authenticated request before
        self._token_write_lock = asyncio.Lock()

    async def _get_new_token(self) -> str:
        """get a new JWT token from the oauth server"""
        _logger.debug("Retrieving a new token")
        token, _ = await self._oauth2client.get_access_token("code", grant_type="client_credentials")
        return token

    async def _get_oauth_token(self) -> str:
        """
        encapsulates the oauth part, such that it's e.g. easily mockable in tests
        :returns the oauth token
        """
        async with self._token_write_lock:
            if self._token is None:
                _logger.info("Initially retrieving a new token")
                self._token = await self._get_new_token()
            elif not self._token_is_valid(self._token):
                _logger.info("Token is not valid anymore, retrieving a new token")
                self._token = await self._get_new_token()
            else:
                _logger.debug("Token is still valid, reusing it")
        return self._token
