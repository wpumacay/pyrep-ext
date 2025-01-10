from __future__ import annotations

from typing import Any, Optional, Union

import numpy as np

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

    def get_position(self, relative_to: Optional[Object] = None) -> np.ndarray:
        """
        Returns the position this object with respect to a given object. If no
        relative object is given, then the position of this object is with
        respect to the world frame.

        Parameters
        ----------
            relative_to: Optional[Object]
                A reference to an object used as reference frame

        Returns
        -------
            np.ndarray
                The position of this object measured respect to the given frame
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()
        position = self._sim_api.getObjectPosition(self._handle, rel_to_handle)
        return np.array(position, dtype=np.float64)

    def set_position(
        self,
        position: Union[list, np.ndarray],
        relative_to: Optional[Object] = None,
        reset_dynamics: bool = True,
    ) -> None:
        """
        Sets the position of this object with respect to the given object. If no
        object is given as reference, then the position is in world space.

        Parameters
        ----------
            position: Union[list, np.ndarray]
                The position of the object
            relative_to: Optional[Object]
                An object to be used as reference to set the position
            reset_dynamics: bool
                Whether or not to reset the dynamics after moving the object
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()

        self._sim_api.setObjectPosition(
            self._handle, list(position), rel_to_handle
        )
