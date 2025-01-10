import time
from pathlib import Path

import numpy as np

from pyrep_ext.objects.shape import Shape
from pyrep_ext.pyrep import PyRep


def main() -> int:
    scene_filepath = str(Path(__file__).parent / "ex_test_scene.ttt")

    pr = PyRep()
    pr.launch(scene_filepath, responsive_ui=False, headless=False)
    pr.set_simulation_timestep(0.001)
    pr.start()

    # Get the handle to the sphere in the scene
    sphere = Shape("sphere")

    print(f"sphere handle: {sphere.get_handle()}")
    print(f"sphere position: {sphere.get_position()}")
    print(f"sphere orientation: {sphere.get_orientation()}")

    _, _, z = sphere.get_position()

    for _ in range(1000):
        x, y = 0.5 * np.cos(time.time()), 0.5 * np.sin(time.time())
        sphere.set_position([x, y, z])
        pr.step()

    pr.stop()
    pr.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
