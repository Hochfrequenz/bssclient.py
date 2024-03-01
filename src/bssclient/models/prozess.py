"""
models for BSS Prozess
"""

import json
import logging
import xml.etree.ElementTree as ET
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

_logger = logging.getLogger(__name__)


class Prozess(BaseModel):
    """
    a bss prozess
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID
    status: str
    status_text: str = Field(alias="statusText")
    typ: str
    ausloeser: str
    externe_id: str = Field(alias="externeId")
    marktlokation: str | None = None
    ide_referenz: str | None = Field(alias="ideReferenz", default=None)
    transaktionsgrund: str | None = None
    ausloeser_daten: str = Field(alias="ausloeserDaten")
    antwort_status: str | None = Field(alias="antwortStatus", default=None)
    einheit: str | None = None
    messlokation: str | None = None
    zaehlernummer: str | None = None

    @computed_field
    # @property
    def deserialized_ausloeser(self) -> dict | ET.Element:
        """
        the self.ausloeser_daten is either a json (boneycomb) or a topcom XML.
        """
        try:
            return json.loads(self.ausloeser_daten)
        except json.decoder.JSONDecodeError:
            # if the xml parsing throws an exception, too, I don't know what to do with it yet
            xml_element: ET.Element = ET.fromstring(self.ausloeser_daten)
            return xml_element
