#!/usr/bin/env sh

TOOLS=/opt/caffe/build/tools

/usr/bin/mpirun -n 1 \
$TOOLS/caffe train --solver=../models/mementos_untrimmednet_solver.prototxt --weights=../models/bn_inception_flow_init.caffemodel

echo "Done."

