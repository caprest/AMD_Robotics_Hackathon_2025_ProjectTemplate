from pathlib import Path

from .dataset.dataset import Dataset
from .robot.so101 import So101Robot
from .pipeline import InferencePipeline
from .policy.act import ActPolicy
from .sheet.sheet import Sheet
from .robot.sim import SimRobot
from .robot.dummy import DummyRobot
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", type=str, nargs="?", default="so101", choices=["so101", "sim", "dummy"]
    )
    return parser.parse_args()


def main():
    args = parse_args()
    mode = args.mode

    print("Running in mode: ", mode)

    # robot
    if mode == "so101":
        robot = So101Robot()
    elif mode == "sim":
        dataset = Dataset("abemii/cmaj_scale_dataset_v2")
        robot = SimRobot(dataset=dataset)
    elif mode == "dummy":
        dataset = Dataset("abemii/cmaj_scale_dataset_v2")
        robot = DummyRobot(dataset=dataset)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    robot.connect()  # could be in ctor

    # policy
    print("🧭 Loading policy...")
    policy = ActPolicy(
        {
            "z": "abemii/act_so101_cmaj_scale_datset_v6_G_010000_amd_cloud",
            "C4": "abemii/act_so101_cmaj_scale_datset_v6_G_010000_amd_cloud",
            "E4": "abemii/act_so101_cmaj_scale_datset_v6_G_010000_amd_cloud",
            "G4": "abemii/act_so101_cmaj_scale_datset_v6_G_010000_amd_cloud",
        }
    )

    # sheet
    sheet = Sheet()

    # pipeline
    pipeline = InferencePipeline(robot, policy, sheet)

    # running pipeline
    pipeline.run()

    # terminating process
    print("🤖 Disconnecting robot...")
    robot.disconnect()


if __name__ == "__main__":
    main()
