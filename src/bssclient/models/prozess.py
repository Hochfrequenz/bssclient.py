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
    marktlokation: str
    ide_referenz: str = Field(alias="ideReferenz")
    transaktionsgrund: str
    ausloeser_daten: str = Field(alias="ausloeserDaten")
    antwort_status: str = Field(alias="antwortStatus")
    einheit: str
    messlokation: str
    zaehlernummer: str
