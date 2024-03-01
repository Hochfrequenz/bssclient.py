"""
models for Ermittlungsauftrag/Investigation Order
"""

from datetime import datetime
from typing import Literal
from uuid import UUID
from xml.etree.ElementTree import Element

import pytz
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel

from bssclient.models.prozess import Prozess

_berlin = pytz.timezone("Europe/Berlin")


class Notiz(BaseModel):
    """
    Notiz am Ermittlungsauftrag
    """

    autor: str
    zeitpunkt: AwareDatetime | None = None
    inhalt: str
    timestamp: AwareDatetime | None = None
    guid: UUID


class Ermittlungsauftrag(BaseModel):
    """
    an investigation order
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: UUID
    flat_id: str | None = Field(alias="flatId", default=None)
    """
    the external ID of the respective Wohneinheit
    """
    marktlokation_id: str | None = Field(alias="marktlokationId", default=None)
    """
    malo id
    """
    messlokation_id: str | None = Field(alias="messlokationId", default=None)
    """
    melo id
    """
    zaehlernummer: str | None = Field(alias="zaehlernummer", default=None)
    vertrag_id: UUID = Field(alias="vertragId")
    """
    ID of the respective netzvertrag
    """
    lieferbeginn: AwareDatetime
    lieferende: AwareDatetime | None
    notizen: list[Notiz]
    kategorie: Literal["Ermittlungsauftrag"]
    prozess: Prozess

    def get_vertragsbeginn_from_boneycomb_or_topcom(self) -> AwareDatetime:
        """
        reads the vertragsbeginn from the boneycomb or topcom data (nested deep into the prozess)
        """
        ausloeser = self.prozess.deserialized_ausloeser
        if isinstance(ausloeser, dict):
            return datetime.fromisoformat(ausloeser["transaktionsdaten"]["vertragsbeginn"])
        if isinstance(ausloeser, Element):
            date_str = ausloeser.find("lieferbeginn").text
            if date_str is None:
                raise ValueError("lieferbeginn not found in topcom XML")
            naive_date = datetime.strptime(date_str, "%Y-%m-%d")
            aware_date = _berlin.localize(naive_date)  # everyone hates implicit timezones
            return pytz.utc.normalize(aware_date)
        raise NotImplementedError(f"ausloeser {ausloeser} is not implemented")


class _ListOfErmittlungsauftraege(RootModel[list[Ermittlungsauftrag]]):
    pass
