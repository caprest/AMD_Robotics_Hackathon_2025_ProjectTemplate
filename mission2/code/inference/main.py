from .policy.const import TransitionType
from .sheet.keyboard import KeyboardState
from .sheet.scores import TrasitionSequence
from .dataset.dataset import Dataset
from .robot.so101 import So101Robot
from .pipeline import InferencePipeline
from .policy.act import ActPolicy
from .sheet.sheet import Sheet
from .robot.sim import SimRobot
from .robot.dummy import DummyRobot
import argparse
import curses


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", type=str, nargs="?", default="so101", choices=["so101", "sim", "dummy"]
    )
    parser.add_argument(
        "--input_mode",
        action="store",
        default="sheet",
        choices=["sheet", "keyboard"],
        help="Input mode",
    )
    return parser.parse_args()


def setup_robot(mode: str):
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
    return robot


def setup_policy():
    print("🧭 Loading policy...")
    return ActPolicy(
        {
            TransitionType.C_TO_E: "abemii/act_so101_cmaj_scale_dataset_v8_CE_move_005000_amd_cloud",
            TransitionType.C_TO_G: "abemii/act_so101_cmaj_scale_dataset_v8_CE_move_005000_amd_cloud",
        }
    )


def run_sheet_mode(args):
    """Run with sheet music input (no curses needed)."""
    print("Running in mode:", args.mode)
    print("🎻 Sheet mode")

    robot = setup_robot(args.mode)
    robot.connect()

    policy = setup_policy()
    sheet = Sheet(score=TrasitionSequence)

    pipeline = InferencePipeline(robot, policy, sheet=sheet, keyboard=None, stdscr=None)
    pipeline.run()

    print("🤖 Disconnecting robot...")
    robot.disconnect()


def run_keyboard_mode(stdscr, args):
    """Run with keyboard input (curses mode)."""
    stdscr.clear()
    stdscr.addstr(0, 0, f"Running in mode: {args.mode}")
    stdscr.addstr(
        1, 0, "🎮 Keyboard mode - Press 'e' for C→E, 'g' for C→G, 'q' to quit"
    )
    stdscr.refresh()

    robot = setup_robot(args.mode)
    robot.connect()

    policy = setup_policy()
    keyboard = KeyboardState(stdscr)

    pipeline = InferencePipeline(
        robot, policy, sheet=None, keyboard=keyboard, stdscr=stdscr
    )
    pipeline.run()

    stdscr.addstr(10, 0, "🤖 Disconnecting robot...")
    stdscr.refresh()
    robot.disconnect()


def main():
    args = parse_args()

    if args.input_mode == "sheet":
        run_sheet_mode(args)
    elif args.input_mode == "keyboard":
        curses.wrapper(lambda stdscr: run_keyboard_mode(stdscr, args))
    else:
        raise ValueError(f"Invalid input mode: {args.input_mode}")


if __name__ == "__main__":
    main()
