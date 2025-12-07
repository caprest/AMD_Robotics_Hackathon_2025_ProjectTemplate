#!/usr/bin/env bash

NAME="cmaj_scale_dataset_v6_E_push"
STEPS=100000
DATSET_REPO_ID="abemii/${NAME}"
JOB_NAME="act_so101_${NAME}_${STEPS}_amd_cloud"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

source .env

lerobot-train \
  --dataset.repo_id=${DATSET_REPO_ID} \
  --batch_size=64 \
  --save_freq=5000 \
  --log_freq=50 \
  --steps=${STEPS} \
  --output_dir=${OUTPUT_DIR} \
  --job_name=${JOB_NAME} \
  --policy.device=cuda \
  --policy.type=act \
  --policy.repo_id=${JOB_NAME} \
  --wandb.enable=true \
  --policy.push_to_hub=true
  # --dataset.video_backend=pyav \  # 遅くなるから使わないほうが良い。