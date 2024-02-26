"""
TMDS in v2 supports RFC6902 JSON Patch. This module contains the patching logic.
"""

import json
from typing import Callable, TypeVar

import jsonpatch  # type:ignore[import]# https://github.com/stefankoegl/python-json-patch/issues/158
from pydantic import BaseModel

Entity = TypeVar("Entity", bound=BaseModel)


def build_json_patch_document(current_state: Entity, changes: list[Callable[[Entity], None]]) -> jsonpatch.JsonPatch:
    """
    creates a json patch (RFC6902) that contains all the changes applied to current_state.
    Note that the result is not stable, i.e. the order of operations in the patch may vary.
    See https://github.com/stefankoegl/python-json-patch/issues/151
    """
    current_state_dict = json.loads(current_state.model_dump_json(by_alias=True))
    # we create a deep copy of the original object
    # using construct rather than model_validate to bypass validation
    new_state = current_state.model_copy(deep=True)
    for change in changes:
        change(new_state)
    new_state_dict = json.loads(new_state.model_dump_json(by_alias=True))
    patch = jsonpatch.make_patch(current_state_dict, new_state_dict)
    return patch
