"""
general aufgabe related models
"""

from typing import Literal

from pydantic import BaseModel

_AufgabenTypen = Literal["Gpidentifizieren", "Ermittlungsauftrag", "Test", "MarktnachrichtenFreigeben", "Unbekannt"]


class AufgabeStats(BaseModel):
    """
    response model auf /api/Aufgabe/stats/
    """

    stats: dict[
        _AufgabenTypen,
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

    def get_sum(self, AufgabenTyp: _AufgabenTypen) -> int:
        """
        get the sum of all statuses for the given AufgabenTyp
        """
        return sum(self.stats[AufgabenTyp]["status"].values())
