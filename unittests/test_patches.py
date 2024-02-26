"""
tests the bare JSON patch logic (no requests)
"""

import uuid
from datetime import datetime, timezone
from typing import Callable

import pytest
from jsonpatch import JsonPatch  # type:ignore[import]

from bssclient.models.netzvertrag import Bo4eVertrag, Netzvertrag, Vertragsstatus
from bssclient.models.patches import build_json_patch_document


def _set_netzvertrag_vertragsbeginn(nv: Netzvertrag, vertragsbeginn: datetime) -> None:
    assert nv.bo_model is not None
    nv.bo_model.vertragsbeginn = vertragsbeginn


def _set_netzvertrag_status(nv: Netzvertrag, status: Vertragsstatus) -> None:
    assert nv.bo_model is not None
    nv.bo_model.vertragstatus = status


@pytest.mark.parametrize(
    "old_nv, changes, expected",
    [
        pytest.param(
            Netzvertrag(
                id=uuid.uuid4(),
                boModel=Bo4eVertrag.construct(vertragsbeginn=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
            ),
            [lambda x: _set_netzvertrag_vertragsbeginn(x, datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc))],
            JsonPatch([]),
            id="nothing to do",
        ),
        pytest.param(
            Netzvertrag(
                id=uuid.uuid4(),
                boModel=Bo4eVertrag.construct(vertragsbeginn=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
            ),
            [lambda x: _set_netzvertrag_vertragsbeginn(x, datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc))],
            JsonPatch([{"op": "replace", "path": "/boModel/vertragsbeginn", "value": "2024-01-01T00:00:00Z"}]),
            id="change one property",
        ),
        pytest.param(
            Netzvertrag(
                id=uuid.uuid4(),
                boModel=Bo4eVertrag.construct(
                    vertragsbeginn=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    vertragstatus=Vertragsstatus.AKTIV,
                ),
            ),
            [
                lambda x: _set_netzvertrag_vertragsbeginn(x, datetime(2023, 7, 1, 0, 0, 0, tzinfo=timezone.utc)),
                lambda x: _set_netzvertrag_status(x, Vertragsstatus.STORNIERT),
            ],
            JsonPatch(
                [
                    {"op": "replace", "path": "/boModel/vertragsbeginn", "value": "2023-07-01T00:00:00Z"},
                    {"op": "replace", "path": "/boModel/vertragstatus", "value": "STORNIERT"},
                ]
            ),
            id="change 2 properties",
        ),
    ],
)
def test_netzvertrag_patch_creation(
    old_nv: Netzvertrag, changes: list[Callable[[Netzvertrag], None]], expected: JsonPatch
):
    actual = build_json_patch_document(old_nv, changes)
    actual_patch = actual.patch
    expected_patch = expected.patch
    assert isinstance(actual_patch, list)
    assert actual_patch is not None
    assert actual_patch == expected_patch or list(reversed(actual_patch)) == expected_patch
    # why the hack is the last assertion necessary?
    # see https://github.com/stefankoegl/python-json-patch/issues/151
    # note the last assertion only is guaranteed for lists up to 2 entries.
    # for longer lists you might find the test to be flaky.
