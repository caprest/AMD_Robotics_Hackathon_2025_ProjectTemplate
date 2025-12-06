#!/usr/bin/env bash

NAME="cmaj_scale_dataset_v2"
STEPS=100000
DATSET_REPO_ID="abemii/${NAME}"
JOB_NAME="act_so101_${NAME}_${STEPS}_amd_cloud"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

source .env

lerobot-train \
  --dataset.repo_id=${DATSET_REPO_ID} \
  --batch_size=128 \
  --steps=${STEPS} \
  --output_dir=${OUTPUT_DIR} \
  --job_name=${JOB_NAME} \
  --policy.device=cuda \
  --policy.type=act \
  --policy.push_to_hub=false \
  --wandb.enable=true
  --policy.push_to_hub=${OUTPUT_DIR}/checkpoints/${STEPS}/pretrained_model