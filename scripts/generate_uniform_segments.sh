#!/usr/bin/env sh

DATASET_NAME="Mementos"
PATH_TO_FRAMES='D:\TU Delft\Master 19-20\VicarVision\data\MementosTVL1\test\frames'
PATH_TO_SPLIT_DEF='D:\TU Delft\Master 19-20\VicarVision\data\MementosTVL1\test\train_defs'
PATH_TO_OUTPUT='D:\TU Delft\Master 19-20\VicarVision\data\MementosTVL1\test\annotations'
LEVEL=1

python ../data/build_file_lists.py $DATASET_NAME "$PATH_TO_FRAMES" "$PATH_TO_SPLIT_DEF" --level $LEVEL --out_list_path "$PATH_TO_OUTPUT"