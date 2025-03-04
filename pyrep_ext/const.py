from enum import Enum

from .core import sim_const as sim

BASE_SCENE = "pyrep_base.ttt"


class PrimitiveShape(Enum):
    CUBOID = 0
    SPHERE = 1
    CYLINDER = 2
    CONE = 3


class ObjectType(Enum):
    ALL = sim.sim_handle_all
    SHAPE = sim.sim_object_shape_type
    JOINT = sim.sim_object_joint_type
    DUMMY = sim.sim_object_dummy_type
    PROXIMITY_SENSOR = sim.sim_object_proximitysensor_type
    GRAPH = sim.sim_object_graph_type
    CAMERA = sim.sim_object_camera_type
    VISION_SENSOR = sim.sim_object_visionsensor_type
    VOLUME = sim.sim_object_volume_type
    MILl = sim.sim_object_mill_type
    FORCE_SENSOR = sim.sim_object_forcesensor_type
    LIGHT = sim.sim_object_light_type
    MIRROR = sim.sim_object_mirror_type
    OCTREE = sim.sim_object_octree_type


class JointType(Enum):
    REVOLUTE = sim.sim_joint_revolute_subtype
    PRISMATIC = sim.sim_joint_prismatic_subtype
    SPHERICAL = sim.sim_joint_spherical_subtype


class JointMode(Enum):
    KINEMATIC = sim.sim_jointmode_kinematic
    DEPENDENT = sim.sim_jointmode_dependent
    DYNAMIC = sim.sim_jointmode_dynamic


class JointControlMode(Enum):
    FREE = sim.sim_jointdynctrl_free
    FORCE = sim.sim_jointdynctrl_force
    VELOCITY = sim.sim_jointdynctrl_velocity
    POSITION = sim.sim_jointdynctrl_position
    SPRING = sim.sim_jointdynctrl_spring
    CALLBACK = sim.sim_jointdynctrl_callback


class ConfigurationPathAlgorithms(Enum):
    BiTRRT = "BiTRRT"
    BITstar = "BITstar"
    BKPIECE1 = "BKPIECE1"
    CForest = "CForest"
    EST = "EST"
    FMT = "FMT"
    KPIECE1 = "KPIECE1"
    LazyPRM = "LazyPRM"
    LazyPRMstar = "LazyPRMstar"
    LazyRRT = "LazyRRT"
    LBKPIECE1 = "LBKPIECE1"
    LBTRRT = "LBTRRT"
    PDST = "PDST"
    PRM = "PRM"
    PRMstar = "PRMstar"
    pRRT = "pRRT"
    pSBL = "pSBL"
    RRT = "RRT"
    RRTConnect = "RRTConnect"
    RRTstar = "RRTstar"
    SBL = "SBL"
    SPARS = "SPARS"
    SPARStwo = "SPARStwo"
    STRIDE = "STRIDE"
    TRRT = "TRRT"


class TextureMappingMode(Enum):
    PLANE = sim.sim_texturemap_plane
    CYLINDER = sim.sim_texturemap_cylinder
    SPHERE = sim.sim_texturemap_sphere
    CUBE = sim.sim_texturemap_cube


class PerspectiveMode(Enum):
    ORTHOGRAPHIC = 0
    PERSPECTIVE = 1


class RenderMode(Enum):
    OPENGL = sim.sim_rendermode_opengl
    OPENGL_AUXILIARY = sim.sim_rendermode_auxchannels
    OPENGL_COLOR_CODED = sim.sim_rendermode_colorcoded
    POV_RAY = sim.sim_rendermode_povray
    EXTERNAL = sim.sim_rendermode_extrenderer
    EXTERNAL_WINDOWED = sim.sim_rendermode_extrendererwindowed
    OPENGL3 = sim.sim_rendermode_opengl3
    OPENGL3_WINDOWED = sim.sim_rendermode_opengl3windowed


class Verbosity(Enum):
    NONE = "none"
    ERRORS = "errors"
    WARNINGS = "warnings"
    LOAD_INFOS = "loadinfos"
    SCRIPT_ERRORS = "scripterrors"
    SCRIPT_WARNINGS = "scriptwarnings"
    SCRIPT_INFOS = "scriptinfos"
    INFOS = "infos"
    DEBUG = "debug"
    TRACE = "trace"
    TRACE_LUA = "tracelua"
    TYRACE_ALL = "traceall"


PYREP_SCRIPT_TYPE = sim.sim_scripttype_addonscript
