from .robot.const import So101MotorPosNames
from .robot.base import BaseRobot
from .policy.act import ActPolicy
from .sheet.sheet import Sheet
import torch
import tqdm


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
        sheet: Sheet,
    ):
        self.robot = robot
        self.policy = policy
        self.sheet = sheet

    def run(self):
        print("🏃‍♀️ Running inference pipeline...")

        self.sheet.start()
        _iter = 0
        while True:
            print("iter: ", _iter)
            _iter += 1

            note_num = self.sheet.tick_note()
            if note_num is None:
                print("🎼 Sheet ended")
                break
            note = self.sheet.number_to_note(note_num)
            print("note:", note)
            if note is None:
                # DO NOTHING!
                continue

            observation = self.robot.get_observation()
            action = self.policy.inference(observation, note)
            if action is None:
                print(f"No action for note: {note}")
                continue

            action_dict = _postprocess_action(action)
            self.robot.send_action(action_dict)
            self.robot.on_end_of_frame()
