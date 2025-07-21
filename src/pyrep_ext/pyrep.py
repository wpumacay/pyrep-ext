import os
import sys
import threading
import time
import warnings
from pathlib import Path
from typing import Union

import numpy as np

from pyrep_ext.const import Verbosity
from pyrep_ext.core import utils
from pyrep_ext.core.errors import PyRepError
from pyrep_ext.core.sim import SimBackend
from pyrep_ext.core.sim_const import (
    sim_floatparam_simulation_time_step,
    sim_handle_scene,
)


class PyRep(object):
    def __init__(self):
        self.running = False
        self._ui_thread = None
        self._handles_to_objects = {}
        self._step_lock = utils.step_lock
        self._sim_api = None  # check later
        self._shutting_down = False

        if "COPPELIASIM_ROOT" not in os.environ:
            raise PyRepError(
                "COPPELIASIM_ROOT not defined. See installation instructions."
            )
        self._coppeliasim_root = os.environ["COPPELIASIM_ROOT"]
        if not os.path.exists(self._coppeliasim_root):
            raise PyRepError(
                "COPPELIASIM_ROOT was not a correct path. "
                "See installation instructions"
            )

    def _run_responsive_ui_thread(self) -> None:
        while True:
            with utils.step_lock:
                if self._shutting_down or self._sim_backend.simGetExitRequest():
                    break
                self._sim_backend.simLoop()
            time.sleep(0.01)
        # If the exit request was from the UI, then call shutdown, otherwise
        # shutdown caused this thread to terminate.
        if not self._shutting_down:
            self.shutdown()

    def launch(
        self,
        scene_file: Union[str, Path] = "",
        headless: bool = False,
        responsive_ui: bool = False,
        blocking: bool = False,
        verbosity: Verbosity = Verbosity.NONE,
    ) -> None:
        """Launches CoppeliaSim.

        Launches the UI thread, waits until the UI thread has finished, this
        results in the current thread becoming the simulation thread.

        :param scene_file: The scene file to load. Empty string for empty scene.
        :param headless: Run CoppeliaSim in simulation mode.
        :param responsive_ui: If True, then a separate thread will be created to
            asynchronously step the UI of CoppeliaSim. Note, that will reduce
            the responsiveness of the simulation thread.
        :param blocking: Causes CoppeliaSim to launch as if running the default
            c++ client application. This is causes the function to block.
            For most users, this will be set to False.
        :param verbosity: The verbosity level for CoppeliaSim.
            Usually Verbosity.NONE or Verbosity.LOAD_INFOS.
        """
        abs_scene_file: str = ""
        scene_file_valid: bool = False
        if isinstance(scene_file, str):
            abs_scene_file = os.path.abspath(scene_file)
            scene_file_valid = len(scene_file) > 0
        elif isinstance(scene_file, Path):
            abs_scene_file = str(scene_file.resolve())
            scene_file_valid = scene_file.exists()

        if scene_file_valid and not os.path.isfile(abs_scene_file):
            raise PyRepError("Scene file does not exist: %s" % scene_file)
        self._sim_backend = SimBackend()
        self._ui_thread = self._sim_backend.create_ui_thread(
            headless, responsive_ui
        )
        self._ui_thread.start()
        self._sim_api = self._sim_backend.simInitialize(
            self._coppeliasim_root, verbosity.value
        )
        if scene_file_valid:
            self._sim_api.loadScene(abs_scene_file)

        if blocking:
            while not self._sim_backend.simGetExitRequest():
                self._sim_backend.simLoop(True)
            self.shutdown()
        elif responsive_ui:
            self._responsive_ui_thread = threading.Thread(
                target=self._run_responsive_ui_thread
            )
            self._responsive_ui_thread.daemon = True
            try:
                self._responsive_ui_thread.start()
            except (KeyboardInterrupt, SystemExit):
                if not self._shutting_down:
                    self.shutdown()
                sys.exit()
            self.step()
        else:
            self.step()

    def shutdown(self) -> None:
        """Shuts down the CoppeliaSim simulation."""
        if self._ui_thread is None:
            raise PyRepError(
                "CoppeliaSim has not been launched. Call launch first."
            )
        if self._ui_thread is not None:
            # self._shutting_down = True
            self.stop()
            self.step_ui()
            self._sim_backend.simDeinitialize()
            # sim.simExtPostExitRequest()
            # sim.simExtSimThreadDestroy()
            # self._ui_thread.join()
            # if self._responsive_ui_thread is not None:
            #     self._responsive_ui_thread.join()
            # # CoppeliaSim crashes if new instance opened too quickly
            # # after shutdown.
            # # TODO: A small sleep stops this for now.
            # time.sleep(0.1)
        self._ui_thread = None
        # self._shutting_down = False

    def start(self) -> None:
        """Starts the physics simulation if it is not already running."""
        if self._ui_thread is None:
            raise PyRepError(
                "CoppeliaSim has not been launched. Call launch first."
            )
        if not self.running:
            self._sim_backend.simStartSimulation()
            self.running = True

    def stop(self) -> None:
        """Stops the physics simulation if it is running."""
        if self._ui_thread is None:
            raise PyRepError(
                "CoppeliaSim has not been launched. Call launch first."
            )
        if self.running:
            self._sim_backend.simStopSimulation()
            self.running = False

    def step(self) -> None:
        """Execute the next simulation step.

        If the physics simulation is not running, then this will only update
        the UI.
        """
        with self._step_lock:
            self._sim_backend.simStep()

    def step_ui(self) -> None:
        """Update the UI.

        This will not execute the next simulation step, even if the physics
        simulation is running.
        This is only applicable when PyRep was launched without a responsive UI.
        """
        with self._step_lock:
            self._sim_backend.simLoop()

    def set_simulation_timestep(self, dt: float) -> None:
        if self._sim_api is not None:
            self._sim_api.setFloatParameter(
                sim_floatparam_simulation_time_step, dt
            )
            if not np.allclose(self.get_simulation_timestep(), dt):
                warnings.warn(
                    "pyrep::set_simulation_timestep >>> Could not change "
                    f"simulation timestep to value {dt}. You may need to "
                    'change it to "custom dt" using simulation settings dialog.'
                )

    def get_simulation_timestep(self) -> float:
        if self._sim_api is not None:
            return self._sim_api.getSimulationTimeStep()
        return 0

    def set_realtime_sim(self, realtime: bool = True) -> None:
        if self._sim_api is not None:
            self._sim_api.setBoolProperty(
                sim_handle_scene, "realtimeSimulation", realtime
            )

    def import_model(self, filepath: str) -> None:
        if self._sim_api is not None:
            _ = self._sim_api.loadModel(filepath)
