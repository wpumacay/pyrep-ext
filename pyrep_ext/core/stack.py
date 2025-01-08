import ctypes
from typing import Any, Dict, List, Optional, Tuple, Union

from .lib import const, cpllib


def read_null(stackHandle: int) -> None:
    if cpllib.simGetStackItemType(stackHandle, -1) == const.sim_stackitem_null:
        cpllib.simPopStackItem(stackHandle, 1)
        return None
    else:
        raise RuntimeError("expected nil")


def read_bool(stackHandle: int) -> bool:
    value = ctypes.c_bool()
    if cpllib.simGetStackBoolValue(stackHandle, ctypes.byref(value)) == 1:
        cpllib.simPopStackItem(stackHandle, 1)
        return value.value
    else:
        raise RuntimeError("expected bool")


def read_int(stackHandle: int) -> int:
    value = ctypes.c_int()
    if cpllib.simGetStackInt32Value(stackHandle, ctypes.byref(value)) == 1:
        cpllib.simPopStackItem(stackHandle, 1)
        return value.value
    else:
        raise RuntimeError("expected int")


def read_long(stackHandle: int) -> int:
    value = ctypes.c_longlong()
    if cpllib.simGetStackInt64Value(stackHandle, ctypes.byref(value)) == 1:
        cpllib.simPopStackItem(stackHandle, 1)
        return value.value
    else:
        raise RuntimeError("expected int64")


def read_double(stackHandle: int) -> float:
    value = ctypes.c_double()
    if cpllib.simGetStackDoubleValue(stackHandle, ctypes.byref(value)) == 1:
        cpllib.simPopStackItem(stackHandle, 1)
        return value.value
    else:
        raise RuntimeError("expected double")


def read_string(
    stackHandle: int, encoding: Optional[str] = None
) -> Union[str, bytes]:
    string_size = ctypes.c_int()
    string_ptr = cpllib.simGetStackStringValue(
        stackHandle, ctypes.byref(string_size)
    )
    value = ctypes.string_at(string_ptr, string_size.value)
    cpllib.simPopStackItem(stackHandle, 1)
    if encoding:
        try:
            value = value.decode(encoding)
        except UnicodeDecodeError:
            pass
    cpllib.simReleaseBuffer(string_ptr)
    return value


def read_dict(stackHandle: int) -> dict:
    d = dict()
    info = cpllib.simGetStackTableInfo(stackHandle, 0)
    if (
        info != const.sim_stack_table_map
        and info != const.sim_stack_table_empty
    ):
        raise RuntimeError("expected a map")
    oldsz = cpllib.simGetStackSize(stackHandle)
    cpllib.simUnfoldStackTable(stackHandle)
    n = (cpllib.simGetStackSize(stackHandle) - oldsz + 1) // 2
    for i in range(n):
        cpllib.simMoveStackItemToTop(stackHandle, oldsz - 1)
        k = read_value(stackHandle)
        cpllib.simMoveStackItemToTop(stackHandle, oldsz - 1)
        d[k] = read_value(stackHandle)
    return d


def read_list(stackHandle: int) -> list:
    lst = list()
    oldsz = cpllib.simGetStackSize(stackHandle)
    cpllib.simUnfoldStackTable(stackHandle)
    n = (cpllib.simGetStackSize(stackHandle) - oldsz + 1) // 2
    for i in range(n):
        cpllib.simMoveStackItemToTop(stackHandle, oldsz - 1)
        read_value(stackHandle)
        cpllib.simMoveStackItemToTop(stackHandle, oldsz - 1)
        lst.append(read_value(stackHandle))
    return lst


def read_table(stackHandle: int, typeHint: Optional[str] = None) -> Any:
    sz = cpllib.simGetStackTableInfo(stackHandle, 0)
    if typeHint == "list" or sz >= 0:
        return read_list(stackHandle)
    elif typeHint == "dict" or sz in (
        const.sim_stack_table_map,
        const.sim_stack_table_empty,
    ):
        return read_dict(stackHandle)


def read_value(stackHandle: int, typeHint: Optional[str] = None) -> Any:
    if typeHint == "null":
        return read_null(stackHandle)
    elif typeHint in ("float", "double"):
        return read_double(stackHandle)
    elif typeHint == "bool":
        return read_bool(stackHandle)
    elif typeHint == "string":
        return read_string(stackHandle, encoding="utf-8")
    elif typeHint == "buffer":
        return read_string(stackHandle, encoding=None)
    elif typeHint in ("table", "list", "dict"):
        return read_table(stackHandle, typeHint)
    elif typeHint in ("int", "long"):
        return read_long(stackHandle)

    itemType = cpllib.simGetStackItemType(stackHandle, -1)
    if itemType == const.sim_stackitem_null:
        return read_null(stackHandle)
    if itemType == const.sim_stackitem_double:
        return read_double(stackHandle)
    if itemType == const.sim_stackitem_bool:
        return read_bool(stackHandle)
    if itemType == const.sim_stackitem_string:
        return read_string(stackHandle, encoding="utf-8")
    if itemType == const.sim_stackitem_table:
        return read_table(stackHandle, typeHint)
    if itemType == const.sim_stackitem_integer:
        return read_long(stackHandle)
    raise RuntimeError(f"unexpected stack item type: {itemType} ({typeHint=})")


def read(stackHandle: int, typeHints: Optional[Tuple] = None) -> Any:
    stack_size = cpllib.simGetStackSize(stackHandle)
    tuple_data = []
    for i in range(stack_size):
        cpllib.simMoveStackItemToTop(stackHandle, 0)
        if typeHints and len(typeHints) > i:
            value = read_value(stackHandle, typeHints[i])
        else:
            value = read_value(stackHandle)
        tuple_data.append(value)
    cpllib.simPopStackItem(stackHandle, 0)  # clear all
    return tuple(tuple_data)


def write_null(stackHandle: int, _: Any) -> None:
    cpllib.simPushNullOntoStack(stackHandle)


def write_double(stackHandle: int, value: float) -> None:
    cpllib.simPushDoubleOntoStack(stackHandle, value)


def write_bool(stackHandle: int, value: bool) -> None:
    cpllib.simPushBoolOntoStack(stackHandle, value)


def write_int(stackHandle: int, value: int) -> None:
    cpllib.simPushInt32OntoStack(stackHandle, value)


def write_long(stackHandle: int, value: int) -> None:
    cpllib.simPushInt64OntoStack(stackHandle, value)


def write_string(
    stackHandle: int, value: str, encoding: Optional[str] = "utf-8"
) -> None:
    if encoding:
        value = value.encode(encoding)  # type: ignore
    cpllib.simPushStringOntoStack(stackHandle, value, len(value))


def write_dict(stackHandle: int, value: Dict) -> None:
    cpllib.simPushTableOntoStack(stackHandle)
    for k, v in value.items():
        write_value(stackHandle, k)
        write_value(stackHandle, v)
        cpllib.simInsertDataIntoStackTable(stackHandle)


def write_list(stackHandle: int, value: List) -> None:
    cpllib.simPushTableOntoStack(stackHandle)
    for i, v in enumerate(value):
        write_value(stackHandle, i + 1)
        write_value(stackHandle, v)
        cpllib.simInsertDataIntoStackTable(stackHandle)


def write_value(
    stackHandle: int, value: Any, typeHint: Optional[str] = None
) -> None:
    if typeHint == "null":
        return write_null(stackHandle, value)
    elif typeHint in ("float", "double"):
        return write_double(stackHandle, value)
    elif typeHint == "bool":
        return write_bool(stackHandle, value)
    elif typeHint in ("int", "long"):
        return write_long(stackHandle, value)
    elif typeHint == "buffer":
        return write_string(stackHandle, value, encoding=None)  # type: ignore
    elif typeHint == "string":
        return write_string(stackHandle, value, encoding="utf-8")
    elif typeHint == "dict":
        return write_dict(stackHandle, value)
    elif typeHint == "list":
        return write_list(stackHandle, value)

    if value is None:
        return write_null(stackHandle, value)
    elif isinstance(value, float):
        return write_double(stackHandle, value)
    elif isinstance(value, bool):
        return write_bool(stackHandle, value)
    elif isinstance(value, int):
        return write_long(stackHandle, value)
    elif isinstance(value, bytes):
        return write_string(stackHandle, value, encoding=None)  # type: ignore
    elif isinstance(value, str):
        return write_string(stackHandle, value, encoding="utf-8")
    elif isinstance(value, dict):
        return write_dict(stackHandle, value)
    elif isinstance(value, list):
        return write_list(stackHandle, value)
    raise RuntimeError(f"unexpected type: {type(value)} ({typeHint=})")


def write(
    stackHandle: int, tuple_data: Tuple, typeHints: Optional[Tuple] = None
) -> None:
    for i, value in enumerate(tuple_data):
        if typeHints and len(typeHints) > i:
            write_value(stackHandle, value, typeHints[i])
        else:
            write_value(stackHandle, value)


def debug(stackHandle: int, info: Optional[str] = None) -> None:
    info = "" if info is None else f" {info} "
    n = (70 - len(info)) // 2
    m = 70 - len(info) - n
    print("#" * n + info + "#" * m)
    for i in range(cpllib.simGetStackSize(stackHandle)):
        cpllib.simDebugStack(stackHandle, i)
    print("#" * 70)


def callback(f):
    def wrapper(stackHandle: int):
        from typing import get_args

        inTypes = tuple(
            [
                arg_type.__name__
                for arg, arg_type in f.__annotations__.items()
                if arg != "return"
            ]
        )

        if return_annotation := f.__annotations__.get("return"):
            origin = getattr(return_annotation, "__origin__", None)
            if origin in (tuple, list):  # Handling built-in tuple and list
                outTypes = tuple(
                    [t.__name__ for t in get_args(return_annotation)]
                )
            elif (
                origin
            ):  # Handling other generic types like Tuple, List from typing
                outTypes = (origin.__name__,)
            else:
                outTypes = (return_annotation.__name__,)
        else:
            outTypes = ()

        try:
            inArgs = read(stackHandle, inTypes)
            outArgs = f(*inArgs)
            if outArgs is None:
                outArgs = ()
            elif not isinstance(outArgs, tuple):
                outArgs = (outArgs,)
            write(stackHandle, outArgs, outTypes)
            return 1
        except Exception:
            import traceback

            traceback.print_exc()
            return 0

    return wrapper
