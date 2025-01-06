from pathlib import Path

from pyrep_ext.pyrep import PyRep


def main() -> int:
    scene_filepath = str(Path(__file__).parent / "ex_test_scene.ttt")

    pr = PyRep()
    pr.launch(scene_filepath)
    pr.start()

    for _ in range(100):
        pr.step()

    pr.stop()
    pr.shutdown()

    return 0

if __name__ == '__main__':
    raise SystemExit(main())





