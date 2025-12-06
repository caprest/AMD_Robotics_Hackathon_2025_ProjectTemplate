from .base import BaseRobot
import torch
from ..dataset.dataset import Dataset


class DummyRobot(BaseRobot):
    """Dummy robot without any physical connection."""

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.sequence_index = 0

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_observation(self) -> dict[str, torch.Tensor]:
        observation = self.dataset[self.sequence_index]
        self.sequence_index += 1
        if self.sequence_index >= len(self.dataset):
            self.sequence_index = 0
        return observation

    def send_action(self, action: dict):
        pass
