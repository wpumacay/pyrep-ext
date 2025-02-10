import numpy as np
from moviepy import ImageSequenceClip
from PIL import Image

from pyrep_ext import MODELS_DIR, SCENES_DIR
from pyrep_ext.objects.joint import Joint
from pyrep_ext.objects.vision_sensor import VisionSensor
from pyrep_ext.pyrep import PyRep


def main() -> int:
    pr = PyRep()
    pr.launch(
        str(SCENES_DIR / "pyrep_base.ttt"), responsive_ui=False, headless=False
    )
    pr.import_model(str(MODELS_DIR / "pendulum.ttm"))
    pr.set_realtime_sim(True)
    pr.set_simulation_timestep(0.005)
    pr.start()

    hinge = Joint("/hinge")
    hinge.set_joint_position(np.random.uniform(-np.pi, np.pi))

    vision_sensor = VisionSensor("main_camera")

    frames = []
    for _ in range(1000):
        pr.step()
        frames.append(vision_sensor.capture_rgb())

    clip = ImageSequenceClip(frames, fps=60)
    clip.write_videofile("sample.mp4", fps=60)

    pr.stop()
    pr.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
