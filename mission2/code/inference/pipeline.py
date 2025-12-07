from .robot.const import So101MotorPosNames
from .robot.base import BaseRobot
from .policy.act import ActPolicy
from .sheet.sheet import Sheet
from .sheet.keyboard import KeyboardState
import torch
from .policy.const import TransitionType


def _postprocess_action(action: torch.Tensor) -> dict:
    assert action.shape == (6,)
    return {
        So101MotorPosNames.SHOULDER_PAN.value: action[0],
        So101MotorPosNames.SHOULDER_LIFT.value: action[1],
        So101MotorPosNames.ELBOW_FLEX.value: action[2],
        So101MotorPosNames.WRIST_FLEX.value: action[3],
        So101MotorPosNames.WRIST_ROLL.value: action[4],
        So101MotorPosNames.GRIPPER.value: action[5],
    }


class InferencePipeline(object):
    def __init__(
        self,
        robot: BaseRobot,
        policy: ActPolicy,
        sheet: Sheet | None,
        keyboard: KeyboardState | None,
        stdscr=None,
    ):
        self.robot = robot
        self.policy = policy
        self.stdscr = stdscr

        self.sheet = sheet
        if self.sheet is not None:
            self.sheet.start()

        self.keyboard = keyboard

        if self.sheet is None and self.keyboard is None:
            raise ValueError("Either sheet or keyboard must be provided")

    def _log(self, row: int, msg: str):
        """Output message - uses curses if available, otherwise print."""
        if self.stdscr is not None:
            self.stdscr.addstr(row, 0, msg.ljust(60))
            self.stdscr.refresh()
        else:
            print(msg)

    def run(self):
        self._log(2, "🏃‍♀️ Running inference pipeline...")

        _iter = 0
        while True:
            if self.keyboard is not None:
                self.keyboard.clear()
                self.keyboard.poll()

                # Check for quit
                if self.keyboard.is_pressed("q"):
                    self._log(8, "👋 Quit requested")
                    break

            _iter += 1
            self._log(3, f"iter: {_iter}")

            note = None

            if self.sheet is not None:
                note_num = self.sheet.tick_note()
                if note_num is None:
                    self._log(8, "🎼 Sheet ended")
                    break
                note = self.sheet.number_to_note(note_num)

            if self.keyboard is not None:
                if self.keyboard.is_pressed("e"):
                    note = TransitionType.C_TO_E
                elif self.keyboard.is_pressed("g"):
                    note = TransitionType.C_TO_G
                else:
                    note = None

            self._log(4, f"note: {note} (type: {type(note).__name__})")

            # Skip rest notes ("z" or 0)
            if note is None or note == "z" or note == 0:
                self._log(5, "⏸️ Skipping rest note")
                continue

            observation = self.robot.get_observation()

            self._log(5, f"🎯 Calling policy with note: {note}")
            action = self.policy.inference(observation, note)
            if action is None:
                self._log(6, f"❌ No action returned for note: {note}")
                continue

            self._log(6, f"✅ Action received, sending to robot...")
            action_dict = _postprocess_action(action)
            self.robot.send_action(action_dict)
            self.robot.on_end_of_frame()
