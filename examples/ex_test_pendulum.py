import numpy as np

from pyrep_ext import SCENES_DIR
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

    for _ in range(3000):
        pr.step()

    pr.stop()
    pr.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
