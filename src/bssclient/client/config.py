"""
contains a class with which the BSS client is instantiated/configured
"""

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator, model_validator
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

    bearer_token: str | None = None
    """
    You may optionally provide a 'hardcoded' bearer token here. As long as its valid, it's used for requests and the
    client id and secret are not used.
    This is useful when you have ways to get a token but not a client id and secret.
    """

    @model_validator(mode="after")
    def check_secret_or_token_is_present(cls, values):  # pylint:disable=no-self-argument
        """
        Ensures that either (id+secret) or a bare token are present
        """
        token_is_present = values.bearer_token is not None and values.bearer_token.strip()
        client_id_and_secret_are_present = (
            values.client_id is not None
            and values.client_id.strip()
            and values.client_secret is not None
            and values.client_secret.strip()
        )
        if not token_is_present and not client_id_and_secret_are_present:
            raise ValueError(
                # pylint:disable=line-too-long
                f"You must provide either cliend id and secret or a bearer token, but not None of both"
            )
