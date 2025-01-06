import argparse
import os.path

from pyrep_ext.core.lib import cpllib, COPPELIASIM_LIBPATH
from pyrep_ext.core.cmdopt import add, read_args

def simThreadFunc():
    cpllib.simInitialize(os.path.dirname(COPPELIASIM_LIBPATH).encode('utf-8'), 0)
    while not cpllib.simGetExitRequest():
        cpllib.simLoop(None, 0)
    cpllib.simDeinitialize()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    add(parser)
    args = parser.parse_args()
    options = read_args(args)

    if args.true_headless:
        simThreadFunc()
    else:
        import threading
        t = threading.Thread(target=simThreadFunc)
        t.start()
        cpllib.simRunGui(options)
        t.join()