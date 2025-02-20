import numpy as np

from pyrep_ext import SCENES_DIR
from pyrep_ext.const import JointControlMode, JointMode
from pyrep_ext.objects.joint import Joint
from pyrep_ext.pyrep import PyRep


def main() -> int:
    scene_filepath = SCENES_DIR / "pyrep_pendulum.ttt"

    pr = PyRep()
    pr.launch(scene_filepath, responsive_ui=False, headless=False)
    pr.set_realtime_sim(True)
    pr.set_simulation_timestep(0.005)
    pr.start()

    hinge = Joint("/hinge")
    hinge.set_joint_position(np.random.uniform(-np.pi, np.pi))
    print(f"joint-type: {hinge.get_joint_type()}")
    print(f"joint-mode: {hinge.get_joint_mode()}")
    print(f"joint-ctrl-mode: {hinge.get_control_mode()}")
    print(f"joint-has-limits: {hinge.has_limits()}")

    hinge.set_joint_limits((-np.pi / 2, np.pi / 2))

    # hinge.set_joint_mode(JointMode.DYNAMIC)
    # hinge.set_control_mode(JointControlMode.POSITION)
    # hinge.set_max_force(10.0)
    # hinge.set_joint_target_position(np.pi / 4)

    print(f"joint-ctrl-mode: {hinge.get_control_mode()}")
    print(f"joint-target-force: {hinge.get_joint_target_force()}")

    for _ in range(3000):
        # print(f"joint's angular velocity: {hinge.get_joint_velocity()}")
        # hinge.set_joint_target_force(np.random.randn())
        pr.step()

    print(hinge)

    pr.stop()
    pr.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
