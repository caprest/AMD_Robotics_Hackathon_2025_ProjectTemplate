from .robot.so101 import So101MotorPosNames
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
    def __init__(self, robot: BaseRobot, policy: ActPolicy, sheet: Sheet):
        self.robot = robot
        self.policy = policy
        self.sheet = sheet

    def run(self):
        print("🏃‍♀️ Running inference pipeline...")

        self.sheet.start()
        while True:
            note = self.sheet.get_note()
            if note is None:
                print("🎼 Sheet ended")
                break

            observation = self.robot.get_observation()
            if "observation.environment_state" not in observation:
                print(f"note: {self.sheet.number_to_note(note)}")
                observation["observation.environment_state"] = torch.tensor(
                    [note], dtype=torch.int64
                )
            action = self.policy.inference(observation)
            action_dict = _postprocess_action(action)
            self.robot.send_action(action_dict)
