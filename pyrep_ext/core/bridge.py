import ctypes
import functools
import sys

from .lib import cpllib, const
from .stack import read, write

def load():
    # add coppeliaSim's pythondir to sys.path:
    pythonDirPtr = cpllib.simGetStringParam(const.sim_stringparam_pythondir)
    pythonDir = ctypes.string_at(pythonDirPtr).decode('utf-8')
    cpllib.simReleaseBuffer(pythonDirPtr)
    if pythonDir not in sys.path:
        sys.path.append(pythonDir)

    # load lua functions for call(), getObject(), etc...:
    call('require', ('scriptClientBridge',))


@functools.cache
def getTypeHints(func):
    # calltip comes from the CoppeliaSim python folder, added to sys.path
    from calltip import FuncDef, VarArgs # type: ignore
    c = call('sim.getApiInfo', [-1, func], (('int', 'string'), ('string')))
    if not c:
        return (None, None)
    c = c.split('\n')[0]
    fd = FuncDef.from_calltip(c)
    inArgs = list(fd.in_args)
    if inArgs and isinstance(inArgs[-1], VarArgs):
        inArgs.pop()
    outArgs = list(fd.out_args)
    if outArgs and isinstance(outArgs[-1], VarArgs):
        outArgs.pop()
    return tuple(tuple(item.type for item in x) for x in (inArgs, outArgs))


def call(func, args, typeHints=None):
    if typeHints is None:
        typeHints = getTypeHints(func)
    stackHandle = cpllib.simCreateStack()
    write(stackHandle, args, typeHints[0])
    s = cpllib.simGetScriptHandleEx(const.sim_scripttype_sandbox, -1, None);
    f = ctypes.c_char_p(f'{func}@lua'.encode('ascii'))
    r = cpllib.simCallScriptFunctionEx(s, f, stackHandle)
    if r == -1:
        if False:
            what = f'simCallScriptFunctionEx({s}, {func!r}, {args!r})'
        else:
            what = 'simCallScriptFunctionEx'
        raise Exception(f'{what} returned -1')
    ret = read(stackHandle, typeHints[1])
    cpllib.simReleaseStack(stackHandle)
    if len(ret) == 1:
        return ret[0]
    elif len(ret) > 1:
        return ret


def getObject(name, _info=None):
    ret = type(name, (), {})
    if not _info:
        _info = call('scriptClientBridge.info', [name])
    for k, v in _info.items(): # type: ignore
        if not isinstance(v, dict):
            raise ValueError('found nondict')
        if len(v) == 1 and 'func' in v:
            if f'{name}.{k}' == 'sim.getScriptFunctions':
                setattr(ret, k, lambda scriptHandle:
                        type('', (object,), {
                            '__getattr__':
                                lambda _, func:
                                    lambda *args:
                                        call('sim.callScriptFunction', (func, scriptHandle) + args)
                        })())
                continue
            setattr(ret, k, lambda *a, func=f'{name}.{k}': call(func, a))
        elif len(v) == 1 and 'const' in v:
            setattr(ret, k, v['const'])
        else:
            setattr(ret, k, getObject(f'{name}.{k}', _info=v))
    return ret


def require(obj):
    call('scriptClientBridge.require', [obj])
    o = getObject(obj)
    return o