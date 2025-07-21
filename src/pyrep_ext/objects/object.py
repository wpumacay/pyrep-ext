from __future__ import annotations

import abc
from typing import Any, List, Optional, Tuple, Union

import numpy as np

from pyrep_ext.const import ObjectType
from pyrep_ext.core import sim_const
from pyrep_ext.core.errors import WrongObjectTypeError
from pyrep_ext.core.sim import SimBackend


class Object(abc.ABC):
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
        self._name: str = self.get_name()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Object):
            raise NotImplementedError
        return self.get_handle() == other.get_handle()

    @abc.abstractmethod
    def _get_requested_type(self) -> ObjectType:
        """
        Abstract method associated with the object type for each subclass. Must
        implement on each subclass of this interface, and return the enum type
        of object that such subclass returns
        """
        pass

    def get_handle(self) -> int:
        """
        Returns the handle of this object. The handle consists in an identifier
        that is unique for each object, and that uniquely represents an object
        in the simulation. Note that this is the initial handle that is assigned
        to the object, and could be invalid. Use `is_valid` to determine the
        validity of this handle

        Returns
        -------
            int
                The unique handle of this object
        """
        return self._handle

    def still_exists(self) -> bool:
        """
        Returns the validity of the current handle for this object. This has the
        effect of checking whether or not this object is still in the scene and
        ready to be simulated.

        Returns
        -------
            bool
                Whether or not this object's handle is still valid
        """
        return self._sim_api.isHandle(self._handle)

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

    def get_pose(self, relative_to: Optional[Object] = None) -> np.ndarray:
        """Get the pose of this object as an array of 3d pos and 4d quaternion

        Note that the pose is relative to the given object reference. If no
        object reference is given, then the pose is measured with respect to the
        world frame

        Parameters
        ----------
            relative_to: Optional[Object]
                An object used as reference to get the pose of the object

        Returns
        -------
            np.ndarray
                The position and orientation of the object into a single array
        """
        position = self.get_position(relative_to=relative_to)
        quaternion = self.get_quaternion(relative_to=relative_to)
        return np.r_[position, quaternion]

    def set_pose(
        self,
        pose: Union[list, np.ndarray],
        relative_to: Optional[Object] = None,
    ) -> None:
        """Sets the position and orientation (quaternion) of an object

        Note that an object can be provided as reference frame. If no object is
        given as reference, then the given pose is measured with respect to the
        world frame.

        Parameters
        ----------
            pose: Union[list, np.ndarray]
                The pose of the object to be set (position and quaternion)
            relative_to: Optional[Object]
                An optional object to be used as reference
        """
        assert len(pose) == 7
        self.set_position(pose[:3], relative_to=relative_to)
        self.set_quaternion(pose[3:], relative_to=relative_to)

    def get_matrix(self, relative_to: Optional[Object] = None) -> np.ndarray:
        """Returns the pose of the object given as a 4x4 transformation matrix

        Parameters
        ----------
            relative_to: Optional[Object]
                An optional object to be used as reference frame

        Returns
        -------
            np.ndarray
                The 4x4 matrix transform of this object
        """
        rel_to_handle = (
            sim_const.sim_handle_world
            if relative_to is None
            else relative_to.get_handle()
        )
        matrix = self._sim_api.getObjectMatrix(self._handle, rel_to_handle)
        matrix_np = np.array(matrix).reshape((3, 4))
        return np.concatenate([matrix_np, [np.array([0, 0, 0, 1])]])

    def set_matrix(
        self, matrix: np.ndarray, relative_to: Optional[Object] = None
    ) -> None:
        """Sets the pose of the object given a 4x4 transformation matrix

        Parameters
        ----------
            matrix: np.ndarray
                The 4x4 transformation matrix to be updated for this object
            relative_to: Optional[Object]
                An optional object to be used as reference frame
        """
        rel_to_handle = (
            sim_const.sim_handle_world
            if relative_to is None
            else relative_to.get_handle()
        )
        self._sim_api.setObjectMatrix(
            self._handle, matrix[:3, :4].reshape((12,)).tolist(), rel_to_handle
        )

    def get_velocity(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns both the linear and angular velocity of this object

        Returns
        -------
            Tuple[np.ndarray, np.ndarray]
                A tuple containing both linear and angular velocity of this body
        """
        linear_vel, angular_vel = self._sim_api.getObjectVelocity(self._handle)
        linear_vel = np.array(linear_vel, dtype=np.float64)
        angular_vel = np.array(angular_vel, dtype=np.float64)
        return linear_vel, angular_vel

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

    def get_name(self) -> str:
        """
        Gets the name alias of this object in the scene

        Returns
        -------
            str
                The name alias of this object in the scene
        """
        return self._sim_api.getObjectAlias(self._handle)

    def set_name(self, name: str) -> None:
        """
        Sets the name of this object in the scene

        Parameters
        ----------
            name: str
                The name to be set for this object in the scene
        """
        self._sim_api.setObjectAlias(self._handle, name)
