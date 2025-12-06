from dataclasses import dataclass
from enum import Enum

import numpy as np
import torch
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.policies.utils import prepare_observation_for_inference
from lerobot.robots.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
from lerobot.robots.utils import make_robot_from_config

from .base import BaseRobot


class So101MotorPosNames(Enum):
    SHOULDER_PAN = "shoulder_pan.pos"
    SHOULDER_LIFT = "shoulder_lift.pos"
    ELBOW_FLEX = "elbow_flex.pos"
    WRIST_FLEX = "wrist_flex.pos"
    WRIST_ROLL = "wrist_roll.pos"
    GRIPPER = "gripper.pos"


class So101CameraNames(Enum):
    ARM = "arm"
    STAND = "stand"
    LIGHT = "light"


@dataclass(frozen=True)
class CameraProfile:
    index_or_path: str | int
    width: int = 640
    height: int = 480
    fps: int = 30

    def to_config(self) -> OpenCVCameraConfig:
        return OpenCVCameraConfig(
            index_or_path=self.index_or_path,
            width=self.width,
            height=self.height,
            fps=self.fps,
        )


def _postprocess_observation(obs: dict) -> dict:
    obs["observation.state"] = np.array(
        [
            obs[So101MotorPosNames.SHOULDER_PAN.value],
            obs[So101MotorPosNames.SHOULDER_LIFT.value],
            obs[So101MotorPosNames.ELBOW_FLEX.value],
            obs[So101MotorPosNames.WRIST_FLEX.value],
            obs[So101MotorPosNames.WRIST_ROLL.value],
            obs[So101MotorPosNames.GRIPPER.value],
        ],
        dtype=np.float32,
    )
    obs["observation.images.arm"] = np.array(
        obs[So101CameraNames.ARM.value], dtype=np.float32
    )
    obs["observation.images.stand"] = np.array(
        obs[So101CameraNames.STAND.value], dtype=np.float32
    )
    obs["observation.images.light"] = np.array(
        obs[So101CameraNames.LIGHT.value], dtype=np.float32
    )

    # remove the motor names from the observation
    for motor_name in So101MotorPosNames:
        obs.pop(motor_name.value)

    obs.pop("arm")
    obs.pop("stand")
    obs.pop("light")
    return obs


class So101Robot(BaseRobot):
    CAMERAS = {
        "arm": CameraProfile("/dev/video6"),
        "stand": CameraProfile("/dev/video8"),
        "light": CameraProfile("/dev/video4"),
    }

    def __init__(self):
        config = SO101FollowerConfig(
            port="/dev/ttyACM1",
            id="tba_follower_arm3",
            cameras={
                name: profile.to_config() for name, profile in self.CAMERAS.items()
            },
        )

        self.robot: SO101Follower = make_robot_from_config(config)

    def connect(self):
        print("🤖 Connecting robot...")
        self.robot.connect()
        if self.robot.is_connected:
            print("✅ Successfully connected SO101 Follower Arm")
        else:
            raise ValueError("❌ Failed to connect SO101 Follower Arm")

    def get_observation(self) -> dict[str, torch.Tensor]:
        obs = self.robot.get_observation()
        obs = _postprocess_observation(obs)
        obs = prepare_observation_for_inference(obs, "cuda")
        return obs

    def disconnect(self):
        self.robot.disconnect()

    def send_action(self, action: dict):
        return self.robot.send_action(action)
