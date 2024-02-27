"""
general aufgabe related models
"""

from typing import Literal

from pydantic import BaseModel


class AufgabeStats(BaseModel):
    """
    response model auf /api/Aufgabe/stats/
    """

    stats: dict[
        Literal["Gpidentifizieren", "Ermittlungsauftrag", "Test", "MarktnachrichtenFreigeben", "Unbekannt"],
        dict[
            Literal["status"],
            dict[
                Literal[
                    "Angelegt",
                    "Beendet",
                    "Abgebrochen",
                    "Offen",
                    "Faellig",
                    "InBearbeitung",
                    "Ausstehend",
                    "Geloest",
                    "Wartend",
                    "NichtErmittelbar",
                ],
                int,
            ],
        ],
    ]
