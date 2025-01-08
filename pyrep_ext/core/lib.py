import os
import platform
from ctypes import (
    CFUNCTYPE,
    POINTER,
    c_bool,
    c_char_p,
    c_double,
    c_int,
    c_longlong,
    c_ubyte,
    c_void_p,
    cdll,
)
from dataclasses import dataclass

from .errors import PyRepError

c_void = None
c_int_p = POINTER(c_int)
c_bool_p = POINTER(c_bool)
c_double_p = POINTER(c_double)
c_longlong_p = POINTER(c_longlong)
c_ubyte_p = POINTER(c_ubyte)
c_callbackfn_p = CFUNCTYPE(c_int, c_int)


if "COPPELIASIM_ROOT" not in os.environ:
    raise PyRepError(
        "COPPELIASIM_ROOT not defined. See installation instructions."
    )
COPPELIASIM_ROOT = os.environ["COPPELIASIM_ROOT"]
COPPELIASIM_LIBPATH = ""

plat = platform.system()
if plat == "Windows":
    raise NotImplementedError("PyRepExt >> not implemented for Windows yet")
elif plat == "Linux":
    COPPELIASIM_LIBPATH = os.path.join(COPPELIASIM_ROOT, "libcoppeliaSim.so")
elif plat == "Darwin":
    raise NotImplementedError("PyRepExt >> not implemented for MacOS yet")


os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = COPPELIASIM_ROOT

cpllib = cdll.LoadLibrary(COPPELIASIM_LIBPATH)
cpllib.simRunGui.argtypes = [c_int]
cpllib.simRunGui.restype = c_void
cpllib.simCreateStack.argtypes = []
cpllib.simCreateStack.restype = c_int
cpllib.simReleaseStack.argtypes = [c_int]
cpllib.simReleaseStack.restype = c_int
cpllib.simReleaseBuffer.argtypes = [c_void_p]
cpllib.simReleaseBuffer.restype = c_int
cpllib.simPushStringOntoStack.argtypes = [c_int, c_char_p, c_int]
cpllib.simPushStringOntoStack.restype = c_int
cpllib.simCallScriptFunctionEx.argtypes = [c_int, c_char_p, c_int]
cpllib.simCallScriptFunctionEx.restype = c_int
cpllib.simGetScriptHandleEx.argtypes = [c_int, c_int, c_char_p]
cpllib.simGetScriptHandleEx.restype = c_int
cpllib.simGetStackStringValue.argtypes = [c_int, c_int_p]
cpllib.simGetStackStringValue.restype = c_void_p
cpllib.simInitialize.argtypes = [c_char_p, c_int]
cpllib.simInitialize.restype = c_int
cpllib.simGetExitRequest.argtypes = []
cpllib.simGetExitRequest.restype = c_int
cpllib.simLoop.argtypes = [c_void_p, c_int]
cpllib.simLoop.restype = c_int
cpllib.simDeinitialize.argtypes = []
cpllib.simDeinitialize.restype = c_int
cpllib.simSetStringParam.argtypes = [c_int, c_char_p]
cpllib.simSetStringParam.restype = c_int
cpllib.simSetNamedStringParam.argtypes = [c_char_p, c_char_p, c_int]
cpllib.simSetNamedStringParam.restype = c_int
cpllib.simRegCallback.argtypes = [c_int, c_callbackfn_p]
cpllib.simRegCallback.restype = c_void
cpllib.simCopyStack.argtypes = [c_int]
cpllib.simCopyStack.restype = c_int
cpllib.simPushNullOntoStack.argtypes = [c_int]
cpllib.simPushNullOntoStack.restype = c_int
cpllib.simPushBoolOntoStack.argtypes = [c_int, c_bool]
cpllib.simPushBoolOntoStack.restype = c_int
cpllib.simPushInt32OntoStack.argtypes = [c_int, c_int]
cpllib.simPushInt32OntoStack.restype = c_int
cpllib.simPushInt64OntoStack.argtypes = [c_int, c_longlong]
cpllib.simPushInt64OntoStack.restype = c_int
cpllib.simPushUInt8TableOntoStack.argtypes = [c_int, c_ubyte_p, c_int]
cpllib.simPushUInt8TableOntoStack.restype = c_int
cpllib.simPushInt32TableOntoStack.argtypes = [c_int, c_int_p, c_int]
cpllib.simPushInt32TableOntoStack.restype = c_int
cpllib.simPushInt64TableOntoStack.argtypes = [c_int, c_longlong_p, c_int]
cpllib.simPushInt64TableOntoStack.restype = c_int
cpllib.simPushTableOntoStack.argtypes = [c_int]
cpllib.simPushTableOntoStack.restype = c_int
cpllib.simInsertDataIntoStackTable.argtypes = [c_int]
cpllib.simInsertDataIntoStackTable.restype = c_int
cpllib.simGetStackSize.argtypes = [c_int]
cpllib.simGetStackSize.restype = c_int
cpllib.simPopStackItem.argtypes = [c_int, c_int]
cpllib.simPopStackItem.restype = c_int
cpllib.simMoveStackItemToTop.argtypes = [c_int, c_int]
cpllib.simMoveStackItemToTop.restype = c_int
cpllib.simGetStackItemType.argtypes = [c_int, c_int]
cpllib.simGetStackItemType.restype = c_int
cpllib.simGetStackBoolValue.argtypes = [c_int, c_bool_p]
cpllib.simGetStackBoolValue.restype = c_int
cpllib.simGetStackInt32Value.argtypes = [c_int, c_int_p]
cpllib.simGetStackInt32Value.restype = c_int
cpllib.simGetStackInt64Value.argtypes = [c_int, c_longlong_p]
cpllib.simGetStackInt64Value.restype = c_int
cpllib.simGetStackTableInfo.argtypes = [c_int, c_int]
cpllib.simGetStackTableInfo.restype = c_int
cpllib.simGetStackUInt8Table.argtypes = [c_int, c_char_p, c_int]
cpllib.simGetStackUInt8Table.restype = c_int
cpllib.simGetStackInt32Table.argtypes = [c_int, c_int_p, c_int]
cpllib.simGetStackInt32Table.restype = c_int
cpllib.simGetStackInt64Table.argtypes = [c_int, c_longlong_p, c_int]
cpllib.simGetStackInt64Table.restype = c_int
cpllib.simUnfoldStackTable.argtypes = [c_int]
cpllib.simUnfoldStackTable.restype = c_int
cpllib.simGetStackDoubleValue.argtypes = [c_int, c_double_p]
cpllib.simGetStackDoubleValue.restype = c_int
cpllib.simGetStackDoubleTable.argtypes = [c_int, c_double_p, c_int]
cpllib.simGetStackDoubleTable.restype = c_int
cpllib.simPushDoubleOntoStack.argtypes = [c_int, c_double]
cpllib.simPushDoubleOntoStack.restype = c_int
cpllib.simPushDoubleTableOntoStack.argtypes = [c_int, c_double_p, c_int]
cpllib.simPushDoubleTableOntoStack.restype = c_int
cpllib.simDebugStack.argtypes = [c_int, c_int]
cpllib.simDebugStack.restype = c_int
cpllib.simGetStringParam.argtypes = [c_int]
cpllib.simGetStringParam.restype = c_void_p


@dataclass(frozen=True)
class const:
    sim_stackitem_null: int = 0
    sim_stackitem_double: int = 1
    sim_stackitem_bool: int = 2
    sim_stackitem_string: int = 3
    sim_stackitem_table: int = 4
    sim_stackitem_func: int = 5
    sim_stackitem_userdat: int = 6
    sim_stackitem_thread: int = 7
    sim_stackitem_lightuserdat: int = 8
    sim_stackitem_integer: int = 9

    sim_stack_table_circular_ref: int = -4
    sim_stack_table_not_table: int = -3
    sim_stack_table_map: int = -2
    sim_stack_table_empty: int = 0

    sim_scripttype_main: int = 0
    sim_scripttype_simulation: int = 1
    sim_scripttype_addon: int = 2
    sim_scripttype_customization: int = 6
    sim_scripttype_sandbox: int = 8
    sim_scripttype_passive: int = 9

    sim_scripttype_mainscript: int = 0
    sim_scripttype_childscript: int = 1
    sim_scripttype_addonscript: int = 2
    sim_scripttype_customizationscript: int = 6
    sim_scripttype_sandboxscript: int = 8

    sim_gui_all: int = 0x0FFFF
    sim_gui_headless: int = 0x10000
    sim_gui_none: int = 0x00000

    sim_stringparam_app_arg1: int = 2
    sim_stringparam_additional_addonscript1: int = 11
    sim_stringparam_additional_addonscript2: int = 12
    sim_stringparam_verbosity: int = 121
    sim_stringparam_statusbarverbosity: int = 122
    sim_stringparam_dlgverbosity: int = 123
    sim_stringparam_startupscriptstring: int = 125

    sim_stringparam_pythondir: int = 137
