#!/usr/bin/env sh

TOOLS=/opt/caffe/build/tools

/usr/bin/mpirun -n 1 \
$TOOLS/caffe train --solver=../models/mementos_untrimmednet_solver.prototxt --weights=../models/anet1.2_temporal_untrimmednet_soft_bn_inception.caffemodel

echo "Done."

