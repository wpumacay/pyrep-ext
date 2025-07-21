from typing import Any, Dict, Tuple

import numpy as np
from gymnasium import spaces

from pyrep_ext import MODELS_DIR, SCENES_DIR
from pyrep_ext.const import BASE_SCENE, JointControlMode, JointMode
from pyrep_ext.objects.joint import Joint
from pyrep_ext.objects.shape import Shape
from pyrep_ext.pyrep import PyRep

SIMULATION_DT = 0.005


class PendulumEnv:

    def __init__(
        self,
        render_mode: str = "human",
        headless: bool = False,
        realtime: bool = False,
    ):
        self._render_mode = render_mode

        scene_filepath = SCENES_DIR / BASE_SCENE
        model_filepath = MODELS_DIR / "pendulum.ttm"

        self._pyrep = PyRep()
        self._pyrep.launch(
            scene_file=str(scene_filepath.resolve()),
            responsive_ui=False,
            headless=(self._render_mode == "rgb_array") or headless,
        )
        self._pyrep.import_model(str(model_filepath.resolve()))
        self._pyrep.set_realtime_sim(realtime)
        self._pyrep.set_simulation_timestep(SIMULATION_DT)

        self._jnt_hinge = Joint("/hinge")
        self._jnt_hinge.set_joint_mode(JointMode.DYNAMIC)
        self._jnt_hinge.set_control_mode(JointControlMode.FORCE)

        self._body_mass = Shape("/mass")

        self._action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(1,), dtype=np.float32
        )
        self._observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32
        )

    @property
    def render_mode(self) -> str:
        return self._render_mode

    @property
    def action_space(self) -> spaces.Box:
        return self._action_space

    @property
    def observation_space(self) -> spaces.Box:
        return self._observation_space

    def get_observation(self) -> np.ndarray:
        mass_position = self._body_mass.get_position()
        qpos = self._jnt_hinge.get_joint_position()
        qvel = self._jnt_hinge.get_joint_velocity()
        return np.array([qpos, qvel, mass_position[2]], dtype=np.float64)

    def reset(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        self._jnt_hinge.set_joint_position(np.random.uniform(-np.pi, np.pi))
        self._pyrep.start()
        obs = self.get_observation()
        return obs, {}

    def step(
        self, action: np.ndarray
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if action.shape != self.action_space.shape:
            raise ValueError(
                "Action mismatch, expected {val_exp}, got {val_got}".format(
                    val_exp=self.action_space.shape, val_got=action.shape
                )
            )

        # Set torque directly to the actuated joint
        self._jnt_hinge.set_joint_target_force(action.item())  # type: ignore
        # Take a step in the simulator
        self._pyrep.step()

        obs = self.get_observation()
        return obs, 0.0, False, False, {}

    def close(self) -> None:
        self._pyrep.stop()
        self._pyrep.shutdown()
