from __future__ import annotations

from typing import Union

from pyrep_ext.const import JointControlMode, JointMode, JointType, ObjectType
from pyrep_ext.objects.object import Object


class Joint(Object):

    def __init__(self, name_or_handle: Union[str, int]):
        super().__init__(name_or_handle=name_or_handle)

        self._type = self.get_joint_type()
        self._mode = self.get_joint_mode()
        self._ctrl_mode = self.get_control_mode()

    def _get_requested_type(self) -> ObjectType:
        return ObjectType.JOINT

    def get_joint_position(self) -> float:
        """
        Returns the current value of this joint's position. The value associated
        with this joint depends on the joint's type. For revolute joints, this
        value represents the angle in radians. For prismatic joints, this value
        represents the distance along the axis in meters.

        Returns
        -------
            float
                The value of this joint's position
        """
        return self._sim_api.getJointPosition(self._handle)

    def set_joint_position(self, position: float) -> None:
        """
        Sets the value of this joint's position. The value associated
        with this joint depends on the joint's type. For revolute joints, this
        value represents the angle in radians. For prismatic joints, this value
        represents the distance along the axis in meters.

        Parameters
        ----------
            position: float
                The value to be set for this joint's position

        """
        self._sim_api.setJointPosition(self._handle, position)

    def get_joint_velocity(self) -> float:
        """
        Returns the current joint's velocity

        Returns
        -------
            float
                The value of the joint's velocity (linear or angular velocity
                depending on the joint type).
        """
        return self._sim_api.getJointVelocity(self._handle)

    def get_joint_type(self) -> JointType:
        """
        Returns the type of this joint

        Returns
        -------
            JointType
                The type of joint
        """
        return JointType(self._sim_api.getJointType(self._handle))

    def get_joint_mode(self) -> JointMode:
        """
        Gets the mode of this joint. This value could be Kinematic, Dependent,
        or Dynamic. According to this mode, the joint can be further configured
        in various control modes. For further reference check CoppeliaSim's docs
        here: https://manual.coppeliarobotics.com/en/jointModes.htm

        Returns
        -------
            JointMode
                The operation mode of this joint
        """
        mode, _ = self._sim_api.getJointMode(self._handle)
        return JointMode(mode)

    def set_joint_mode(self, jnt_mode: JointMode) -> None:
        """
        Sets the operation mode of this joint. The argument can be Kinematic,
        Dependent, or Dynamic. According to this mode, the joint can be further
        configured in various control modes. For further reference check
        CoppeliaSim's docs here:
        https://manual.coppeliarobotics.com/en/jointModes.htm

        Parameters
        ----------
            jnt_mode: JointMode
                The operation mode for this joint
        """

        self._sim_api.setJointMode(self._handle, int(jnt_mode.value), 0)

    def get_control_mode(self) -> JointControlMode:
        """
        Returns the control mode of this joint, which is applicable when in
        Dynamic mode. When in dynamic mode, the joint can be configured to the
        following control modes: FREE, FORCE, VELOCITY, POSITION, SPRING and
        CALLBACK.

        Returns
        -------
            JointControlMode
                The control mode of this joint, if configured as Dynamic
        """
        ctrl_mode = self._sim_api.getIntProperty(self._handle, "dynCtrlMode")
        return JointControlMode(ctrl_mode)

    def set_control_mode(self, ctrl_mode: JointControlMode) -> None:
        """
        Sets the Dynamics Control Mode for this joint. For further reference
        check CoppeliSim's documentation here:
        https://manual.coppeliarobotics.com/en/jointModes.htm

        Parameters
        ----------
            ctrl_mode: JointControlMode
                The dynamics control mode for this joint. This mode is used when
                the operation mode for this joint is set to DYNAMIC.
        """
        self._sim_api.setIntProperty(
            self._handle, "dynCtrlMode", ctrl_mode.value
        )

    def set_joint_target_position(self, position: float) -> None:
        """
        Sets the joint's desired position if working in POSITION control mode

        Parameters
        ----------
            position: float
                The desired position for this joint
        """
        self._sim_api.setJointTargetPosition(self._handle, position)

    def get_joint_target_force(self) -> float:
        """
        Returns the maximum force|torque that can be applied at this joint

        Returns
        -------
            float
                The maximum force|torque that can be applied at this joint
        """
        return self._sim_api.getJointTargetForce(self._handle)

    def set_joint_target_force(self, forceOrTorque: float) -> None:
        """
        Sets the target force at this joint. This quantity's meaning depends on
        the control mode of this joint. If using FORCE mode, then this value
        represents the actual force|torque that is applied at this joint. If
        using POSITION mode, then this represents the maximum force|torque that
        can be applied at this joint

        Parameters
        ----------
            forceOrTorque: float
                The force|torque value for the target force at this joint
        """
        self._sim_api.setJointTargetForce(self._handle, forceOrTorque)

    def __repr__(self) -> str:
        return (
            "Joint<\n"
            f"  name: {self._name}\n"
            f"  type: {self._type}\n"
            f"  mode: {self._mode}\n"
            f"  ctrlmode: {self._ctrl_mode}\n"
            ">\n"
        )
