from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader.config_so101_leader import SO101LeaderConfig
from lerobot.teleoperators.so101_leader.so101_leader import SO101Leader
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun

import datetime
import time
import json
import os
import argparse
import sys
import numpy as np
from typing import Any
from lerobot.robots import Robot
from lerobot.teleoperators import Teleoperator


import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Any

from lerobot.cameras import (  # noqa: F401
    CameraConfig,  # noqa: F401
)
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig  # noqa: F401
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig  # noqa: F401
from lerobot.configs import parser
from lerobot.configs.policies import PreTrainedConfig
from lerobot.datasets.image_writer import safe_stop_image_writer
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.pipeline_features import aggregate_pipeline_dataset_features, create_initial_features
from lerobot.datasets.utils import build_dataset_frame, combine_feature_dicts
from lerobot.datasets.video_utils import VideoEncodingManager
from lerobot.policies.factory import make_policy, make_pre_post_processors
from lerobot.policies.pretrained import PreTrainedPolicy
from lerobot.policies.utils import make_robot_action
from lerobot.processor import (
    PolicyAction,
    PolicyProcessorPipeline,
    RobotAction,
    RobotObservation,
    RobotProcessorPipeline,
    make_default_processors,
    IdentityProcessorStep,
)
from lerobot.processor.rename_processor import rename_stats
from lerobot.robots import (  # noqa: F401
    so101_follower,
)
from lerobot.teleoperators import (  # noqa: F401
    so101_leader,
    koch_leader,
    so100_leader,
)
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop
from lerobot.utils.constants import ACTION, OBS_STR
from lerobot.utils.control_utils import (
    is_headless,
    predict_action,
    sanity_check_dataset_name,
    sanity_check_dataset_robot_compatibility,
)
from lerobot.utils.import_utils import register_third_party_devices
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import (
    get_safe_torch_device,
    init_logging,
    log_say,
)
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data


NUM_EPISODES = 1 
FPS = 30
EPISODE_TIME_SEC = 5
RESET_TIME_SEC = 8
TASK_DESCRIPTION = "My task description"

import sys
import termios
import tty
import select
import time


class KeyWatcher:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        # もとの設定を保存
        self._old_attrs = termios.tcgetattr(self.fd)

        # 非カノニカル + エコーオフにする
        new_attrs = termios.tcgetattr(self.fd)
        new_attrs[3] = new_attrs[3] & ~(termios.ICANON | termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSADRAIN, new_attrs)

        self._p_hit_since_last = False

    def restore(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self._old_attrs)

    def poll(self):
        """この周期中に押されたキーを全部読む。p があればフラグ立て。"""
        # stdin に何か来ているか確認（タイムアウト0でノンブロッキング）
        while True:
            r, _, _ = select.select([sys.stdin], [], [], 0.0)
            if not r:
                break
            ch = sys.stdin.read(1)
            if ch == "p":
                self._p_hit_since_last = True
            # 他のキーを使いたければここに追加する

    def consume_p_hit(self) -> bool:
        """前回の consume 以降に p が押されていたかを返し、フラグをクリア。"""
        hit = self._p_hit_since_last
        self._p_hit_since_last = False
        return hit


watcher = KeyWatcher()




def init_keyboard_listener():
    """
    Initializes a non-blocking keyboard listener for real-time user interaction.

    This function sets up a listener for specific keys (right arrow, left arrow, escape) to control
    the program flow during execution, such as stopping recording or exiting loops. It gracefully
    handles headless environments where keyboard listening is not possible.

    Returns:
        A tuple containing:
        - The `pynput.keyboard.Listener` instance, or `None` if in a headless environment.
        - A dictionary of event flags (e.g., `exit_early`) that are set by key presses.
    """
    # Allow to exit early while recording an episode or resetting the environment,
    # by tapping the right arrow key '->'. This might require a sudo permission
    # to allow your terminal to monitor keyboard events.
    events = {}
    events["exit_early"] = False
    events["rerecord_episode"] = False
    events["stop_recording"] = False
    events["p_pushing"] = False

    if is_headless():
        logging.warning(
            "Headless environment detected. On-screen cameras display and keyboard inputs will not be available."
        )
        listener = None
        return listener, events

    # Only import pynput if not in a headless environment
    from pynput import keyboard

    def on_press(key):
        try:
            if key == keyboard.Key.right:
                print("Right arrow key pressed. Exiting loop...")
                events["exit_early"] = True
            elif key == keyboard.Key.left:
                print("Left arrow key pressed. Exiting loop and rerecord the last episode...")
                events["rerecord_episode"] = True
                events["exit_early"] = True
            elif key == keyboard.Key.esc:
                print("Escape key pressed. Stopping data recording...")
                events["stop_recording"] = True
                events["exit_early"] = True
            elif hasattr(key, "char") and key.char == "p":
                print("Key 'p' pressed. ")
                events["p_pushing"] = True
        except Exception as e:
            print(f"Error handling key press: {e}")
    def on_release(key):
        try:
            if hasattr(key, "char") and key.char == "p":
                print("Key 'p' released. ")
                events["p_pushing"] = False
        except Exception as e:
            print(f"Error handling key release: {e}")

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    return listener, events


@safe_stop_image_writer
def record_loop(
    robot: Robot,
    events: dict,
    fps: int,
    teleop_action_processor: RobotProcessorPipeline[
        tuple[RobotAction, RobotObservation], RobotAction
    ],  # runs after teleop
    robot_action_processor: RobotProcessorPipeline[
        tuple[RobotAction, RobotObservation], RobotAction
    ],  # runs before robot
    robot_observation_processor: RobotProcessorPipeline[
        RobotObservation, RobotObservation
    ],  # runs after robot
    dataset: LeRobotDataset | None = None,
    teleop: Teleoperator | list[Teleoperator] | None = None,
    preprocessor: PolicyProcessorPipeline[dict[str, Any], dict[str, Any]] | None = None,
    postprocessor: PolicyProcessorPipeline[PolicyAction, PolicyAction] | None = None,
    control_time_s: int | None = None,
    single_task: str | None = None,
    display_data: bool = False,
):
    policy=None
    if dataset is not None and dataset.fps != fps:
        raise ValueError(f"The dataset fps should be equal to requested fps ({dataset.fps} != {fps}).")

    teleop_arm = teleop_keyboard = None

    timestamp = 0
    start_episode_t = time.perf_counter()
    while timestamp < control_time_s:
        start_loop_t = time.perf_counter()

        if events["exit_early"]:
            events["exit_early"] = False
            break

        # Get robot observation
        obs = robot.get_observation()

        # Applies a pipeline to the raw robot observation, default is IdentityProcessor
        obs_processed = robot_observation_processor(obs)

        act = teleop.get_action()

        # Applies a pipeline to the raw teleop action, default is IdentityProcessor
        # Convert tuple to dictionary for processor
        act_processed_teleop = teleop_action_processor((act,obs))


        # Applies a pipeline to the action, default is IdentityProcessor
        action_values = act_processed_teleop
        robot_action_to_send = robot_action_processor((act_processed_teleop, obs))

        # Send action to robot
        # Action can eventually be clipped using `max_relative_target`,
        # so action actually sent is saved in the dataset. action = postprocessor.process(action)
        # TODO(steven, pepijn, adil): we should use a pipeline step to clip the action, so the sent action is the action that we input to the robot.
        _sent_action = robot.send_action(robot_action_to_send)

        watcher.poll()

        # この周期で p が押されていたか？
        if watcher.consume_p_hit():
            keyboard_state = np.array([1.0], dtype=np.float32)  # 'p' key is pressed
        else:
            keyboard_state = np.array([0.0], dtype=np.float32)  # 'p' key is not pressed
        print(f"Keyboard state: {keyboard_state}")

        # Write to dataset
        if dataset is not None:
            observation_frame = build_dataset_frame(dataset.features, obs_processed, prefix=OBS_STR)
            action_frame = build_dataset_frame(dataset.features, action_values, prefix=ACTION)
            frame = {
                **observation_frame, **action_frame, "task": single_task,
                "input.keyboard": keyboard_state,  

             }
            dataset.add_frame(frame)

        if display_data:
            log_rerun_data(observation=obs_processed, action=action_values)

        dt_s = time.perf_counter() - start_loop_t
        busy_wait(1 / fps - dt_s)

        timestamp = time.perf_counter() - start_episode_t




# Create the robot and teleoperator configurations

def load_robot_config():
    # Load camera configurations from JSON file
    camera_config = {}
    config_path = os.path.join(os.path.dirname(__file__), "camera_config.json")
    with open(config_path, "r") as f:
        camera_config_json = json.load(f)
    for key, value in camera_config_json.items():
        camera_config[key] = OpenCVCameraConfig(**value)
    
    # Create robot configuration
    robot_config = SO101FollowerConfig(
        port=os.environ["ROBOT_PORT"], 
        id=os.environ["ROBOT_ID"],
        cameras=camera_config
    )
    
    # Create teleoperator configuration
    teleop_config = SO101LeaderConfig(
        port=os.environ["TELEOP_PORT"],
        id=os.environ["TELEOP_ID"]
    )
    
    return robot_config, teleop_config

def beep(times=1, frequency=500, duration=0.2):
    """Play a simple beep sound using pygame"""
    try:
        import pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        
        for _ in range(times):
            # Generate a simple sine wave
            sample_rate = 22050
            samples = int(sample_rate * duration)
            wave = np.sin(2 * np.pi * frequency * np.arange(samples) / sample_rate)
            # Convert to 16-bit PCM
            wave = (wave * 32767).astype(np.int16)
            # Create sound from mono array
            sound = pygame.sndarray.make_sound(wave)
            sound.play()
            pygame.time.wait(int(duration * 1000))
            if _ < times - 1:
                pygame.time.wait(100)  # Short pause between beeps
    except Exception as e:
        # Fallback to terminal beep
        print(f"Could not play sound: {e}")
        for _ in range(times):
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(0.2)

def init_robot_and_teleop():
    robot_config, teleop_config = load_robot_config()
    robot = SO101Follower(robot_config)
    teleop = SO101Leader(teleop_config)
    
    # Connect to devices
    print(f"Connecting to robot on {robot_config.port}...")
    robot.connect()
    print("Robot connected successfully")
    
    print(f"Connecting to teleoperator on {teleop_config.port}...")
    teleop.connect()
    print("Teleoperator connected successfully")
    
    return robot, teleop

def init_dataset(robot, dataset_name="test-recording"):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    hf_repo_id = f"abemii/{dataset_name}-{timestamp}"
    action_features = hw_to_dataset_features(robot.action_features, "action")
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    KEYBOARD_KEYS = ['p']
    keyboard_features = {
        "input.keyboard": {  
            "dtype": "float32",  
            "shape": (len(KEYBOARD_KEYS),),  # キーの数  
            "names": KEYBOARD_KEYS  
        }  
    }

    dataset_features = {**action_features, **obs_features, **keyboard_features}

    dataset = LeRobotDataset.create(
        repo_id=hf_repo_id,
        fps=FPS,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4,
    )
    return dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_episodes", type=int, default=NUM_EPISODES, help="Number of episodes to record")
    parser.add_argument("--episode_time_sec", type=int, default=EPISODE_TIME_SEC, help="Duration of each episode in seconds")
    parser.add_argument("--reset_time_sec", type=int, default=RESET_TIME_SEC, help="Duration of reset time between episodes in seconds")
    parser.add_argument("--task_description", type=str, default=TASK_DESCRIPTION, help="Description of the task")
    parser.add_argument("--dataset_name", type=str, default="test-recording", help="Dataset name (will be prefixed with 'abemii/', e.g., 'my-task')")
    args = parser.parse_args()

    robot, teleop = init_robot_and_teleop()
    dataset = init_dataset(robot, dataset_name=args.dataset_name)

    # Initialize the keyboard listener and rerun visualization
    _, events = init_keyboard_listener()
    init_rerun(session_name="recording")
    episode_idx = 0

    teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()

    log_say(f"Starting record loop for {args.num_episodes} episodes")
    time.sleep(1) # Short delay before starting
    while episode_idx < args.num_episodes and not events["stop_recording"]:
        beep(1)  # Beep once at episode start

        
        record_loop(
             robot=robot,
             events=events,
             fps=FPS,
             teleop=teleop,
             teleop_action_processor=teleop_action_processor,
             robot_action_processor=robot_action_processor,
             robot_observation_processor=robot_observation_processor,
             dataset=dataset,
             control_time_s=args.episode_time_sec,
             single_task=args.task_description,
             display_data=True,
        )
        beep(2)

        if not events["stop_recording"] and (episode_idx < args.num_episodes - 1 or events["rerecord_episode"]):
            log_say("Reset the environment")
            # Reset environment time without recording (by not passing dataset)
            record_loop(
                robot=robot,
                events=events,
                fps=FPS,
                teleop=teleop,
                teleop_action_processor=teleop_action_processor,
                robot_action_processor=robot_action_processor,
                robot_observation_processor=robot_observation_processor,
                control_time_s=args.reset_time_sec,
                single_task=args.task_description,
                display_data=True,
            )


        dataset.save_episode()
        episode_idx += 1
    
    # Clean up
    log_say("Stop recording")
    robot.disconnect()
    teleop.disconnect()
    dataset.push_to_hub()
    
    # Print dataset repository ID for reference
    print(f"\n{'='*80}")
    print(f"Dataset saved successfully!")
    print(f"Repository ID: {dataset.repo_id}")
    print(f"Total episodes recorded: {dataset.num_episodes}")
    print(f"To view the dataset, run:")
    print(f"  python dump_dataset.py \"{dataset.repo_id}\"")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        main()
    finally:
        watcher.restore()