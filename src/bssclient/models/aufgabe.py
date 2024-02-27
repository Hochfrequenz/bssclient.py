"""
general aufgabe related models
"""

import logging
from typing import Literal

from pydantic import BaseModel

_AufgabenTypen = Literal["Gpidentifizieren", "Ermittlungsauftrag", "Test", "MarktnachrichtenFreigeben", "Unbekannt"]

_logger = logging.getLogger(__name__)


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

    def get_sum(self, aufgaben_typ: _AufgabenTypen) -> int:
        """
        get the sum of all statuses for the given AufgabenTyp
        """
        result = sum(self.stats[aufgaben_typ]["status"].values())
        _logger.debug("sum of %s: %s", aufgaben_typ, result)
        return result
