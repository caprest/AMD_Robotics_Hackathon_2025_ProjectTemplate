from .const import So101MotorPosNames
from abc import ABC, abstractmethod


class BaseRobotLogger(ABC):
    @abstractmethod
    def log_observation(self, obs: dict):
        pass

    @abstractmethod
    def log_action(self, action: dict):
        pass

    @abstractmethod
    def print(self):
        pass


class DummyRobotLogger(BaseRobotLogger):
    def __init__(self):
        pass

    def log_observation(self, obs: dict):
        pass

    def log_action(self, action: dict):
        pass

    def print(self):
        pass


class DebugLogger(BaseRobotLogger):
    def __init__(self):
        self.obs = {}
        self.action = {}

    def log_observation(self, obs: dict):
        # log motor positions
        state = obs["observation.state"].squeeze(0)
        for i, name in enumerate(So101MotorPosNames):
            self.obs[name.value] = state[i]

    def log_action(self, action: dict):
        # log motor actions
        for name in So101MotorPosNames:
            self.action[name.value] = action[name.value]

    def print(self):
        for name in So101MotorPosNames:
            print(f"{name.value}: {self.obs[name.value]} -> {self.action[name.value]}")
