from __future__ import annotations

from pyrep_ext.const import ObjectType
from pyrep_ext.objects.object import Object


class Shape(Object):

    def _get_requested_type(self) -> ObjectType:
        return ObjectType.SHAPE
