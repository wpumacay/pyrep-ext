import threading
from ctypes import c_char_p

from .lib import cpllib, const
from .bridge import load as bridge_load
from .bridge import require as bridge_require


class SimBackend:
    _instance = None

    def __new__(cls):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = super(SimBackend, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    @property
    def sim_api(self):
        return self._sim

    @property
    def sim_ik_api(self):
        return self._sim_ik

    @property
    def sim_ompl_api(self):
        return self._sim_ompl

    @property
    def sim_vision_api(self):
        return self._sim_vision

    @property
    def lib(self):
        return cpllib

    def simInitialize(self, appDir: str, verbosity: str):
        cpllib.simSetStringParam(
            const.sim_stringparam_verbosity, c_char_p(verbosity.encode("utf-8"))
        )
        cpllib.simSetStringParam(
            const.sim_stringparam_statusbarverbosity, c_char_p(verbosity.encode("utf-8"))
        )
        cpllib.simInitialize(c_char_p(appDir.encode("utf-8")), 0)

        bridge_load()

        # fetch CoppeliaSim API sim-namespace functions:
        self._sim = bridge_require("sim")
        self._sim_ik = bridge_require("simIK")
        self._sim_ompl = bridge_require("simOMPL")
        self._sim_vision = bridge_require("simVision")
        v = self._sim.getInt32Param(self._sim.intparam_program_full_version)
        self._coppelia_version = ".".join(
            str(v // 100 ** (3 - i) % 100) for i in range(4)
        )
        return self._sim

    def create_ui_thread(self, headless: bool) -> threading.Thread:
        options = const.sim_gui_headless if headless else const.sim_gui_all
        ui_thread = threading.Thread(target=cpllib.simRunGui, args=(options,))
        ui_thread.daemon = True
        return ui_thread

    def simDeinitialize(self):
        cpllib.simDeinitialize()

    def simGetExitRequest(self) -> bool:
        return bool(cpllib.simGetExitRequest())

    def simLoop(self, step_phys: bool = False):
        # Second value toggles stepIfRunning
        cpllib.simLoop(None, int(not step_phys))

    def simStartSimulation(self):
        if self._sim.getSimulationState() == self._sim.simulation_stopped:
            self._sim.startSimulation()

    def simStep(self):
        if self._sim.getSimulationState() != self._sim.simulation_stopped:
            t = self._sim.getSimulationTime()
            while t == self._sim.getSimulationTime():
                cpllib.simLoop(None, 0)

    def simStopSimulation(self):
        while self._sim.getSimulationState() != self._sim.simulation_stopped:
            self._sim.stopSimulation()
            cpllib.simLoop(None, 0)