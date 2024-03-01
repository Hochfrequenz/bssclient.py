"""
models for BSS Prozess
"""

from uuid import UUID

from pydantic import BaseModel, Field


class Prozess(BaseModel):
    """
    a bss prozess
    """

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
