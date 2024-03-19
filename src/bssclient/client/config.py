"""
contains a class with which the BSS client is instantiated/configured
"""

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from yarl import URL


class BssConfig(BaseModel):
    """
    A class to hold the configuration for the BSS client
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    server_url: URL
    """
    e.g. URL("https://basicsupply.xtk-stage.de/")
    """

    # pylint:disable=no-self-argument
    @field_validator("server_url")
    def validate_url(cls, value):
        """
        check that the value is a yarl URL
        """
        # this (together with the nested config) is a workaround for
        # RuntimeError: no validator found for <class 'yarl.URL'>, see `arbitrary_types_allowed` in Config
        if not isinstance(value, URL):
            raise ValueError("Invalid URL type")
        if len(value.parts) > 2:
            raise ValueError("You must provide a base_url without any parts, e.g. https://basicsupply.xtk-prod.de/")
        return value


class BasicAuthBssConfig(BssConfig):
    """
    configuration of bss with basic auth
    """

    usr: str
    """
    basic auth user name
    """
    pwd: str
    """
    basic auth password
    """

    # pylint:disable=no-self-argument
    @field_validator("usr", "pwd")
    def validate_string_is_not_empty(cls, value):
        """
        Check that no one tries to bypass validation with empty strings.
        If we had wanted that you can omit values, we had used Optional[str] instead of str.
        """
        if not value.strip():
            raise ValueError("my_string cannot be empty")
        return value


class OAuthBssConfig(BssConfig):
    """
    configuration of bss with oauth
    """

    client_id: str
    """
    client id for OAuth
    """
    client_secret: str
    """
    client secret for auth password
    """

    token_url: HttpUrl
    """
    Url of the token endpoint; e.g. 'https://lynqtech-dev-auth-server.auth.eu-central-1.amazoncognito.com/oauth2/token'
    """

    # pylint:disable=no-self-argument
    @field_validator("client_id", "client_secret")
    def validate_string_is_not_empty(cls, value):
        """
        Check that no one tries to bypass validation with empty strings.
        If we had wanted that you can omit values, we had used Optional[str] instead of str.
        """
        if not value.strip():
            raise ValueError("my_string cannot be empty")
        return value
