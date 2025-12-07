import argparse
import os.path as osp
import random
import tempfile

import numpy as np
from lerobot.datasets.dataset_tools import (add_features, delete_episodes,
                                            merge_datasets, modify_features,
                                            remove_feature)
from lerobot.datasets.lerobot_dataset import LeRobotDataset

tone_dict = {
    "abemii/test-20251206_172803": 3,  # C
    "abemii/g_1st-20251206_181550": 7,  # G
    "abemii/e_2nd-20251206_185255": 5,  # E
}

NEW_NAME = "abemii/cmaj_scale_dataset_v2"

PREV_FRAMES = 45  # 1.5 seconds at 30fps
POST_FRAMES = 30  # 1.0 seconds at 30fps


# to numpy array
def to_numpy_array(dataset, column_name):
    return np.array([item[column_name] for item in dataset.hf_dataset])


tmp_dir = tempfile.TemporaryDirectory()

dataset_concat_list = []
for name, tone_num in tone_dict.items():
    # Hubからデータセットを読み込み
    dataset = LeRobotDataset(name)

    values_keyboard = to_numpy_array(dataset, "input.keyboard")
    values_frame_index = to_numpy_array(dataset, "frame_index")
    values_episode_index = to_numpy_array(dataset, "episode_index")

    # for each episode_index, find the first frame_index where keyboard == 1.0
    # episode ごとに処理
    unique_episodes = np.unique(values_episode_index)

    # 出力結果（元と同じ長さの 0/1 配列）
    new_flags = np.zeros_like(values_keyboard, dtype=np.float32)

    for ep in unique_episodes:
        # 該当 episode のインデックスを取り出す
        mask = values_episode_index == ep
        ep_indices = np.where(mask)[0]

        # episode 内の keyboard の値
        ep_keyboard = values_keyboard[ep_indices]

        # keyboard==1.0 になる最初の位置を探す
        ones = np.where(ep_keyboard == 1.0)[0]
        if len(ones) == 0:
            # 該当なしなら何もしない
            continue

        first_one_local = ones[0]  # episode 内のローカル index
        first_one_global = ep_indices[first_one_local]  # 全体 index

        # 15 frames 前から first_one_local までを 1 にする
        start_local = max(0, first_one_local - PREV_FRAMES)
        fill_local_indices = ep_indices[start_local : first_one_local + POST_FRAMES]

        # new_flags に書き込む
        new_flags[fill_local_indices] = tone_num

    # 結果を dataset に追加する
    dataset = modify_features(
        dataset,
        add_features={
            "observation.environment_state": (
                new_flags,
                {"dtype": "int64", "shape": (1,), "names": None},
            ),
        },
        remove_features=["input.keyboard"],
        output_dir=osp.join(tmp_dir.name, name.replace("/", "_")),
    )
    # drop the first episode
    dataset = delete_episodes(
        dataset=dataset,
        episode_indices=[0],  # 最初のepisodeを指定
        output_dir=osp.join(tmp_dir.name, name.replace("/", "_") + "_without_first_episode"),
    )
    dataset_concat_list.append(dataset)

dataset_merged = merge_datasets(
    dataset_concat_list, NEW_NAME, output_dir="output/" + NEW_NAME.split("/")[-1]
)
dataset_merged.push_to_hub()

# remove tmp dir
tmp_dir.cleanup()
