from pyrep_ext.suite.pendulum import PendulumEnv


def main() -> int:
    env = PendulumEnv(
        render_mode="human",
        headless=False,
        realtime=True,
    )

    obs = env.reset()
    for _ in range(3000):
        obs, reward, terminate, _, _ = env.step(env.action_space.sample())

    env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
