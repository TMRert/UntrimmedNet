#!/usr/bin/env sh

DATASET_NAME="Mementos"
PATH_TO_DATASET="../data/$DATASET_NAME"
PATH_TO_SPLIT="$PATH_TO_DATASET"
PATH_TO_OUTPUT="$PATH_TO_DATASET/proposals"

python ../data/generate_action_proposals.py "$PATH_TO_SPLIT" --out_dir "$PATH_TO_OUTPUT"