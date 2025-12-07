from .base import BaseRobot
import torch
from ..dataset.dataset import Dataset
from .logger import DebugLogger


class DummyRobot(BaseRobot):
    """Dummy robot without any physical connection."""

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.sequence_index = 0
        self.logger = DebugLogger()

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_observation(self) -> dict[str, torch.Tensor]:
        observation = self.dataset[self.sequence_index]
        self.sequence_index += 1
        if self.sequence_index >= len(self.dataset):
            self.sequence_index = 0
        self.logger.log_observation(observation)

        return observation

    def send_action(self, action: dict):
        self.logger.log_action(action)

    def on_end_of_frame(self):
        self.logger.print()
