#!/usr/bin/env sh

DATASET_NAME="Mementos"
PATH_TO_DATASET="../data/$DATASET_NAME"
PATH_TO_FRAMES="$PATH_TO_DATASET/frames"
PATH_TO_SPLIT_DEF="$PATH_TO_DATASET/train_defs"
PATH_TO_OUTPUT="$PATH_TO_DATASET"
LEVEL=1

python ../data/build_file_lists.py $DATASET_NAME "$PATH_TO_FRAMES" "$PATH_TO_SPLIT_DEF" --level $LEVEL --out_list_path "$PATH_TO_OUTPUT"