Bootstrap: docker
From: nvidia/cuda:10.1-cudnn7-devel-ubuntu16.04

%runscript


%labels
MAINTAINER T.M.rietveld@student.tudelft.nl

%post

DATA_LOCATION=/data
CODE_LOCATION=/src
PACKAGE_LOCATION=/packages
CONDA_DIR=$PACKAGE_LOCATION/conda
CAFFE_ROOT=$PACKAGE_LOCATION/caffe

# Directories for Sherlock
mkdir -p $DATA_LOCATION
mkdir -p $CODE_LOCATION
mkdir -p $PACKAGE_LOCATION
mkdir -p $CONDA_DIR
mkdir -p $CAFFE_ROOT
mkdir -p /scratch-local
mkdir -p /share/PI

# install dependencies
DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        libatlas-base-dev \
        libboost-all-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libprotobuf-dev \
        libsnappy-dev \
        protobuf-compiler \
        openssh-server \
        nano && \
    rm -rf /var/lib/apt/lists/*



# set conda location
PATH=$CONDA_DIR/bin:$PATH
echo 'export PATH=$CONDA_DIR/bin:$PATH' >>$SINGULARITY_ENVIRONMENT

# get conda package
RUN wget --quiet --no-check-certificate https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo "c59b3dd3cad550ac7596e0d599b91e75d88826db132e4146030ef471bb434e9a *Miniconda3-4.2.12-Linux-x86_64.sh" | sha256sum -c - && \
    /bin/bash /Miniconda3-4.2.12-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo export PATH=$CONDA_DIR/bin:'$PATH' > /etc/profile.d/conda.sh


#install python and packages
PYTHON_VERSION=3.6
RUN conda config --append channels conda-forge
RUN conda install -y python=$PYTHON_VERSION && \
    pip install --upgrade pip && \
    pip install --upgrade setuptools


# set caffe root location
cd $CAFFE_ROOT


#fetch repository and install dependencies
CAFFE_CLONE_TAG=custom_caffe
RUN git clone -b ${CAFFE_CLONE_TAG} --depth 1 https://github.com/TMRert/caffe.git .
RUN pip install --upgrade pip
RUN pip install -r python/requirements.txt
RUN git clone https://github.com/NVIDIA/nccl.git


cd nccl && make -j install && cd .. && rm -rf nccl


cd $PACKAGE_LOCATION
#replace cmake as old version has CUDA variable bugs
RUN wget https://github.com/Kitware/CMake/releases/download/v3.16.0/cmake-3.16.0-Linux-x86_64.tar.gz && \
tar xzf cmake-3.16.0-Linux-x86_64.tar.gz -C /opt && \
rm cmake-3.16.0-Linux-x86_64.tar.gz

PATH="/opt/cmake-3.16.0-Linux-x86_64/bin:${PATH}"
echo 'export PATH=/opt/cmake-3.16.0-Linux-x86_64/bin:${PATH}' >>$SINGULARITY_ENVIRONMENT

# run make tests of Caffe
cd $CAFFE_ROOT
RUN cp Makefile.config.example Makefile.config
RUN make all -j"$(nproc)"
RUN make pycaffe -j"$(nproc)"
RUN make test -j"$(nproc)"

PYCAFFE_ROOT=$CAFFE_ROOT/python
PYTHONPATH=$PYCAFFE_ROOT:$PYTHONPATH
PATH=$CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH

echo "$CAFFE_ROOT/build/lib" >> /etc/ld.so.conf.d/caffe.conf && ldconfig
echo 'export PATH=$CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH' >>$SINGULARITY_ENVIRONMENT

cd $CODE_LOCATION

UNTRIMMED_CLONE_TAG=master
git clone -b ${UNTRIMMED_CLONE_TAG} --depth 1 https://github.com/TMRert/UntrimmedNet.git
sed -i 's#http://mcg.nju.edu.cn/models/UntrimmedNet/#https://www.dropbox.com/sh/8yxjj4fbgm2omjd/AADA_ebg-pciLSoC6dUoT1cwa?preview=#g' scripts/get_reference_model_anet.sh
sh scripts/get_reference_model_anet.sh

conda install jupyter pyparsing
conda update -y --all
conda clean -yt


%environment
DATA_LOCATION=/data
CODE_LOCATION=/src
PACKAGE_LOCATION=/packages
CONDA_DIR=$PACKAGE_LOCATION/conda
CAFFE_ROOT=$PACKAGE_LOCATION/caffe
PYCAFFE_ROOT=$CAFFE_ROOT/python
PYTHONPATH=$PYCAFFE_ROOT:$PYTHONPATH
PATH="$CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:/opt/cmake-3.16.0-Linux-x86_64/bin:${PATH}:$CONDA_DIR/bin:$PATH"
