from abc import ABC, abstractmethod

from lerobot.robots.config import RobotConfig
import torch


class BaseRobot(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def get_observation(self) -> dict[str, torch.Tensor]:
        pass

    @abstractmethod
    def send_action(self, action: dict):
        pass
