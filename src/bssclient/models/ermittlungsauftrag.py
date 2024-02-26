"""
models for Ermittlungsauftrag/Investigation Order
"""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel

from bssclient.models.prozess import Prozess


class Notiz(BaseModel):
    """
    Notiz am Ermittlungsauftrag
    """

    autor: str
    zeitpunkt: AwareDatetime | None = None
    inhalt: str
    timestamp: AwareDatetime
    guid: UUID


class Ermittlungsauftrag(BaseModel):
    """
    an investigation order
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: UUID
    flat_id: str = Field(alias="flatId")
    """
    the external ID of the respective Wohneinheit
    """
    marktloaktion_id: str = Field(alias="marktlokationId")
    """
    malo id
    """
    messlokation_id: str = Field(alias="messlokationId")
    """
    melo id
    """
    zaehlernummer: str = Field(alias="zaehlernummer")
    vertrag_id: UUID = Field(alias="vertragId")
    """
    ID of the respective netzvertrag
    """
    lieferbeginn: AwareDatetime
    lieferende: AwareDatetime | None
    notizen: list[Notiz]
    kategorie: Literal["Ermittlungsauftrag"]
    prozess: Prozess


class _ListOfErmittlungsauftraege(RootModel[list[Ermittlungsauftrag]]):
    pass
