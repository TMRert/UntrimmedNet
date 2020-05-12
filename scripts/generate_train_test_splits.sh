#!/usr/bin/env sh

PATH_TO_TRAIN_DEF='D:\TU Delft\Master 19-20\VicarVision\data\MementosTVL1\test\annotations\Mementos'
PATH_TO_OUTPUT=$PATH_TO_TRAIN_DEF

python ../data/generate_uniform_split.py "$PATH_TO_TRAIN_DEF" --out_dir "$PATH_TO_OUTPUT"