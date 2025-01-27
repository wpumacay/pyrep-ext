from __future__ import annotations

from pyrep_ext.const import ObjectType, JointMode, JointType
from pyrep_ext.objects.object import Object


class Joint(Object):

    def _get_requested_type(self) -> ObjectType:
        return ObjectType.JOINT

    def get_joint_position(self) -> float:
        return self._sim_api.getJointPosition(self._handle)

    def set_joint_position(self, position: float) -> None:
        self._sim_api.setJointPosition(self._handle, position)

    def get_joint_type(self) -> JointType:
        return JointType(self._sim_api.getJointType(self._handle))

    def get_joint_mode(self) -> JointMode:
        mode, _ = self._sim_api.getJointMode(self._handle)
        return JointMode(mode)

    def set_joint_mode(self, jnt_mode: JointMode) -> None:
        self._sim_api.setJointMode(self._handle, int(jnt_mode.value), 0)

