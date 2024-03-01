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


class _ListOfErmittlungsauftraege(RootModel[list[Ermittlungsauftrag]]):
    pass
