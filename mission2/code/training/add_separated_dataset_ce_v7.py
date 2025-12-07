import argparse
import os.path as osp
import random
import tempfile

import numpy as np
from lerobot.datasets.dataset_tools import (add_features, delete_episodes,
                                            merge_datasets, modify_features,
                                            remove_feature)
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.v30.augment_dataset_quantile_stats import \
    augment_dataset_with_quantile_stats




data_list = [
    {
        "repo_id": "abemii/c_e_v7-20251207_120435",
        "class": 3,
        "skip": [1],
    },
    #  {
    #      "repo_id": "abemii/g_v5-20251207_101218",
    #      "class": 7,
    #      #  "skip": [1, 2, 3],
    #      "skip": [1, 2],
    #  },
    #  {
    #      "repo_id": "abemii/g_v6_push-20251207_103549",
    #      "class": 7,
    #      "skip": [1, 2, 9, 26, 35],
    #  },
    #  {
    #      "repo_id": "abemii/d_2nd-20251206_222926",
    #      "class": 4,
    #      "skip": [1, 2, 16],
    #  },  # 		hatakeyama	20	1,2,16
    #  {
    #      "repo_id": "abemii/e_3rd-20251206_223742",
    #      "class": 5,
    #      "skip": [1, 8],
    #  },  # 		abe	20	1,8
    # {
    #     "repo_id": "abemii/g_2nd-20251206_225240",
    #     "class": 7,
    #     "skip": [1],
    # },  # 		hatakeyama	20	1
    # {
    #     "repo_id": "abemii/c_3rd-20251206_230456",
    #     "class": 3,
    #     "skip": [1, 18],
    # },  # 		manome	20	1,18
    # {
    #     "repo_id": "abemii/g_3rd-20251206_231711",
    #     "class": 7,
    #     "skip": [1, 2, 13],
    # },  # 		abe	20	1,2,13
    # {
    #     "repo_id": "abemii/c_3rd-20251206_232502",
    #     "class": 3,
    #     "skip": [1, 2],
    # },  # 		abe	20	1,2
    # {
    #     "repo_id": "abemii/d_3rd-20251206_233236",
    #     "class": 4,
    #     "skip": [1, 8, 17],
    # },  # 		hatakeyama	20	1,8,17
    # {
    #     "repo_id": "abemii/e_3rd-20251206_234008",
    #     "class": 5,
    #     "skip": [1, 4, 7],
    # },  # 		hatakeyama	20	1,4,7
    # {
    #     "repo_id": "abemii/g_4th-20251206_235225",
    #     "class": 7,
    #     "skip": [1, 3, 4, 6, 7, 10],
    # },  # abemii/g_4th-20251206_235225		manome	20	1,3,4,6,7,10
]

classes: dict = {
    "CE": 3,
    #  "D": 4,
    #  "E": 5,
    #  "G": 7,
}


# to numpy array
def to_numpy_array(dataset, column_name):
    return np.array([item[column_name] for item in dataset.hf_dataset])


for class_name, class_num in classes.items():
    NEW_NAME = f"abemii/cmaj_scale_dataset_v7_{class_name}_move"

    PREV_FRAMES = 45  # 1.5 seconds at 30fps
    POST_FRAMES = 30  # 1.0 seconds at 30fps

    data_list_filtered = [d for d in data_list if d["class"] == class_num]

    tmp_dir = tempfile.TemporaryDirectory()

    dataset_concat_list = []
    for tone_info in data_list_filtered:
        name = tone_info["repo_id"]
        tone_num = tone_info["class"]
        skip_episodes = tone_info["skip"]
        # Hubからデータセットを読み込み
        dataset = LeRobotDataset(name)

        # values_keyboard = to_numpy_array(dataset, "input.keyboard")
        # values_frame_index = to_numpy_array(dataset, "frame_index")
        # values_episode_index = to_numpy_array(dataset, "episode_index")

        # # for each episode_index, find the first frame_index where keyboard == 1.0
        # # episode ごとに処理
        # unique_episodes = np.unique(values_episode_index)

        # # 出力結果（元と同じ長さの 0/1 配列）
        # new_flags = np.zeros_like(values_keyboard, dtype=np.float32)

        # for ep in unique_episodes:
        #     # 該当 episode のインデックスを取り出す
        #     mask = values_episode_index == ep
        #     ep_indices = np.where(mask)[0]

        #     # episode 内の keyboard の値
        #     ep_keyboard = values_keyboard[ep_indices]

        #     # keyboard==1.0 になる最初の位置を探す
        #     ones = np.where(ep_keyboard == 1.0)[0]
        #     if len(ones) == 0:
        #         # 該当なしなら何もしない
        #         continue

        #     first_one_local = ones[0]  # episode 内のローカル index
        #     first_one_global = ep_indices[first_one_local]  # 全体 index

        #     # 15 frames 前から first_one_local までを 1 にする
        #     start_local = max(0, first_one_local - PREV_FRAMES)
        #     fill_local_indices = ep_indices[start_local : first_one_local + POST_FRAMES]

        #     # new_flags に書き込む
        #     new_flags[fill_local_indices] = tone_num

        # 結果を dataset に追加する
        if skip_episodes:
            episode_indices = [i - 1 for i in skip_episodes]  # 0-based index
            # drop the first episode
            dataset = delete_episodes(
                dataset=dataset,
                episode_indices=episode_indices,  # 最初のepisodeを指定
                output_dir=osp.join(
                    tmp_dir.name, name.replace("/", "_") + "_without_first_episode"
                ),
            )
        dataset = modify_features(
            dataset,
            #  add_features={
            #      "observation.environment_state": (
            #          new_flags,
            #          {"dtype": "int64", "shape": (1,), "names": None},
            #      ),
            #  },
            remove_features=[
                "input.keyboard",
                "observation.images.stand",
                #  "observation.images.light",
            ],
            #  remove_features=["input.keyboard"],
            output_dir=osp.join(tmp_dir.name, name.replace("/", "_")),
            #  repo_id="abemii/tmp_" + name.replace("/", "_")
        )
        #  import pdb; pdb.set_trace()
        dataset_concat_list.append(dataset)

    dataset_merged = merge_datasets(
        dataset_concat_list, NEW_NAME, output_dir="output/" + NEW_NAME.split("/")[-1]
    )
    dataset_merged.push_to_hub()

    # remove tmp dir
    tmp_dir.cleanup()
