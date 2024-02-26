"""
contains a class with which the BSS client is instantiated/configured
"""

from pydantic import BaseModel, ConfigDict, field_validator
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
