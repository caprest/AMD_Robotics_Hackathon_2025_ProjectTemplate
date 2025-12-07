from .logger import DebugLogger
from .base import BaseRobot
import torch
from ..dataset.dataset import Dataset
from .so101 import So101Robot


class SimRobot(BaseRobot):
    """Simulates a robot. It uses dataset to get the observation and send the action to the robot.

    Args:
        dataset_path: Path to the dataset.
    """

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.sequence_index = 0

        self.robot = So101Robot()
        self.logger = DebugLogger()

    def connect(self):
        self.robot.connect()

    def disconnect(self):
        self.robot.disconnect()

    def get_observation(self) -> dict[str, torch.Tensor]:
        observation = self.dataset[self.sequence_index]
        self.sequence_index += 1
        self.logger.log_observation(observation)
        return observation

    def send_action(self, action: dict):
        self.robot.send_action(action)
        self.logger.log_action(action)

    def on_end_of_frame(self):
        self.robot.on_end_of_frame()
