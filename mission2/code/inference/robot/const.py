from enum import Enum


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
