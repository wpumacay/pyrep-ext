from __future__ import annotations

from typing import Any, Optional, Union

from pyrep_ext.const import ObjectType
from pyrep_ext.core.errors import WrongObjectTypeError
from pyrep_ext.core.sim import SimBackend


class Object:
    """Base interface class for CoppeliaSim scene objects"""

    def __init__(
        self,
        name_or_handle: Union[str, int],
        index: int = 0,
        proxy: Optional[Object] = None,
    ):
        self._sim_api: Any = SimBackend().sim_api
        self._handle: int = -1
        if isinstance(name_or_handle, int):
            self._handle = name_or_handle
        else:
            extra = {}
            prefix = "/"
            if index > 0:
                extra["index"] = 0
            if proxy is not None:
                prefix = "./"
                extra["proxy"] = proxy.get_handle()
            try:
                self._handle = self._sim_api.getObject(name_or_handle, extra)
            except Exception:
                try:
                    self._handle = self._sim_api.getObject(
                        prefix + name_or_handle, extra
                    )
                except Exception:
                    raise ValueError(
                        f"Object with name `{name_or_handle}` "
                        "not found in the scene!"
                    )
        assert_type = self._get_requested_type()
        actual_type = ObjectType(self._sim_api.getObjectType(self._handle))
        if actual_type != assert_type:
            raise WrongObjectTypeError(
                f"You requested an object of type {assert_type.name}, but the "
                f"actual type was {actual_type.name}"
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Object):
            raise NotImplementedError
        return self.get_handle() == other.get_handle()

    def _get_requested_type(self) -> ObjectType:
        raise NotImplementedError("Must be overriden.")

    def get_handle(self) -> int:
        return self._handle
