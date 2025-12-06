#!/usr/bin/env bash

NAME="cmaj_scale_dataset_v2"
SUFFIX=""
DATSET_REPO_ID="abemii/${NAME}"
OUTPUT_DIR="outputs/train/act_so101_${NAME}_1ksteps_amd_cloud"
JOB_NAME="act_so101_${NAME}_1ksteps_amd_cloud"

source .env

lerobot-train \
  --dataset.repo_id=${DATSET_REPO_ID} \
  --batch_size=64 \
  --steps=1000 \
  --output_dir=${OUTPUT_DIR} \
  --job_name=${JOB_NAME} \
  --policy.device=cuda \
  --policy.type=act \
  --policy.push_to_hub=false \
  --wandb.enable=true
  --policy.push_to_hub=${OUTPUT_DIR}/checkpoints/001000/pretrained_model
  # --policy.num_environment_classes=8 \