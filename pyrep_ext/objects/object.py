from __future__ import annotations

from typing import Any, List, Optional, Union

import numpy as np

from pyrep_ext.const import ObjectType
from pyrep_ext.core import sim_const
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
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()
        self._sim_api.setObjectPosition(
            self._handle, list(position), rel_to_handle
        )

    def get_orientation(
        self, relative_to: Optional[Object] = None
    ) -> np.ndarray:
        """
        Returns the orientation of this object as a set of Euler angles.

        Note that if no object is given as reference, then the orientation is
        measured with respect to the world frame.

        Parameters
        ----------
            relative_to: Optional[Object]
                An object to be used as reference to get the orientation

        Returns
        -------
            np.ndarray
                The set of Euler angles measured respect to the given frame
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()
        orientation = self._sim_api.getObjectOrientation(
            self._handle, rel_to_handle
        )
        return np.array(orientation, np.float64)

    def set_orientation(
        self,
        orientation: Union[list, np.ndarray],
        relative_to: Optional[Object] = None,
    ) -> None:
        """
        Sets the orientation of this object with respect to a given reference

        Note that if no reference object is given, then the orientation is
        measured with respect to the world frame.

        Parameters
        ----------
            orientation: Union[list, np.ndarray]
                The orientation to be set for this object
            relative_to: Optional[Object]
                An object used as reference to set the orientation of the object
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()
        self._sim_api.setObjectOrientation(
            self._handle, list[orientation], rel_to_handle
        )

    def get_quaternion(
        self, relative_to: Optional[Object] = None
    ) -> np.ndarray:
        """Returns the orientation of this object as a quaternion.

        Note that if no object is given as reference, then the orientation is
        measured with respect to the world frame.

        Parameters
        ----------
            relative_to: Optional[Object]
                An object to use as reference frame

        Returns
        -------
            np.ndarray
                The orientation of the object represented as a 'xyzw' quaternion
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()
        quaternion = self._sim_api.getObjectQuaternion(
            self._handle, rel_to_handle
        )
        return np.array(quaternion, dtype=np.float64)

    def set_quaternion(
        self,
        quaternion: Union[list, np.ndarray],
        relative_to: Optional[Object] = None,
    ) -> None:
        """Sets the orientation of this object using a quaternion representation

        Note that if no object is given as reference, the object orientation is
        set with respect to the world frame. Otherwise, the orientation is set
        with respect to the given object as reference frame.

        Parameters
        ----------
            quaternion: Union[list, np.ndarray]
                The orientation to set given as a quaternion
            relative_to: Optional[Object]
                An object used as reference to set the orientation of the object
        """
        rel_to_handle = -1 if relative_to is None else relative_to.get_handle()
        self._sim_api.setObjectQuaternion(
            self._handle, list(quaternion), rel_to_handle
        )

    def reset_dynamic_object(self) -> None:
        """Dynamically resets an object that is dynamically simulated

        This means that the object representation in the dynamics engine is
        removed, and added again. This can be useful when the set-up of a
        dynamically simulated chain needs to be modified during simulation
        (e.g. joint or shape attachement position/orientation changed).
        It should be noted that calling this on a dynamically simulated object
        might slightly change its position/orientation relative to its parent
        (since the object will be disconnected from the dynamics world in its
        current position/orientation), so the user is in charge of rectifying
        for that.
        """
        self._sim_api.resetDynamicObject(self._handle)

    def get_bounding_box(self) -> List[float]:
        """Gets the bounding box (relative to the object reference frame)

        Returns
        -------
            List[float]
                A list containing the AABB positions
        """
        params = [
            sim_const.sim_objfloatparam_objbbox_min_x,
            sim_const.sim_objfloatparam_objbbox_max_x,
            sim_const.sim_objfloatparam_objbbox_min_y,
            sim_const.sim_objfloatparam_objbbox_max_y,
            sim_const.sim_objfloatparam_objbbox_min_z,
            sim_const.sim_objfloatparam_objbbox_max_z,
        ]
        return [
            self._sim_api.getObjectFloatParam(self._handle, p) for p in params
        ]
