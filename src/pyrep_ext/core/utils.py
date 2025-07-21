from threading import Lock
from typing import List, Tuple

from .sim import SimBackend

step_lock = Lock()


def script_call(
    function_name_at_script_name: str,
    script_handle_or_type: int,
    ints=(),
    floats=(),
    strings=(),
    bytes="",
) -> Tuple[List[int], List[float], List[str], str]:
    """Calls a script function (from a plugin, the main client application,
    or from another script). This represents a callback inside of a script.

    :param function_name_at_script_name: A string representing the function
        name and script name, e.g. myFunctionName@theScriptName. When the
        script is not associated with an object, then just specify the
        function name.
    :param script_handle_or_type: The handle of the script, otherwise the
        type of the script.
    :param ints: The input ints to the script.
    :param floats: The input floats to the script.
    :param strings: The input strings to the script.
    :param bytes: The input bytes to the script (as a string).
    :return: Any number of return values from the called Lua function.
    """
    sim_api = SimBackend().sim_api
    return sim_api.extCallScriptFunction(
        function_name_at_script_name,
        script_handle_or_type,
        list(ints),
        list(floats),
        list(strings),
        bytes,
    )


def _is_in_ipython():
    import builtins

    try:
        return getattr(builtins, "__IPYTHON__", False)
    except NameError:
        pass
    return False

