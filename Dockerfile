ARG cuda_version=10.1
ARG cudnn_version=7
FROM nvidia/cuda:${cuda_version}-cudnn${cudnn_version}-devel

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive
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
        openssh-server && \
    rm -rf /var/lib/apt/lists/*



# set conda location
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV CAFFE_ROOT=/opt/caffe
RUN mkdir $CAFFE_ROOT

# get conda package
RUN wget --quiet --no-check-certificate https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo "c59b3dd3cad550ac7596e0d599b91e75d88826db132e4146030ef471bb434e9a *Miniconda3-4.2.12-Linux-x86_64.sh" | sha256sum -c - && \
    /bin/bash /Miniconda3-4.2.12-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo export PATH=$CONDA_DIR/bin:'$PATH' > /etc/profile.d/conda.sh

# create new user and fix permissions
ENV NB_USER untrimmednet
ENV NB_UID 1000

RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    chown $NB_USER $CONDA_DIR -R && \
    mkdir -p /src && \
    chown $NB_USER /src && \
    chown $NB_USER $CAFFE_ROOT -R



USER $NB_USER

#install python and packages
ARG python_version=3.6
RUN conda config --append channels conda-forge
RUN conda install -y python=${python_version} && \
    pip install --upgrade pip && \
    pip install --upgrade setuptools


# set caffe root location
WORKDIR $CAFFE_ROOT


#fetch repository and install dependencies
ARG CAFFE_CLONE_TAG=custom_caffe
RUN git clone -b ${CAFFE_CLONE_TAG} --depth 1 https://github.com/TMRert/caffe.git .
RUN pip install --upgrade pip
RUN pip install -r python/requirements.txt
RUN git clone https://github.com/NVIDIA/nccl.git

# install nccl and new version cmake and caffe as root
USER root
RUN cd nccl && make -j install && cd .. && rm -rf nccl

#replace cmake as old version has CUDA variable bugs
RUN wget https://github.com/Kitware/CMake/releases/download/v3.16.0/cmake-3.16.0-Linux-x86_64.tar.gz && \
tar xzf cmake-3.16.0-Linux-x86_64.tar.gz -C /opt && \
rm cmake-3.16.0-Linux-x86_64.tar.gz
ENV PATH="/opt/cmake-3.16.0-Linux-x86_64/bin:${PATH}"

# run make tests of Caffe
RUN cp Makefile.config.example Makefile.config
RUN make all -j"$(nproc)"
RUN make pycaffe -j"$(nproc)"
RUN make test -j"$(nproc)"

ENV PYCAFFE_ROOT $CAFFE_ROOT/python
ENV PYTHONPATH $PYCAFFE_ROOT:$PYTHONPATH
ENV PATH $CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH
RUN echo "$CAFFE_ROOT/build/lib" >> /etc/ld.so.conf.d/caffe.conf && ldconfig

WORKDIR /src/untrimmednet
RUN chown $NB_USER /src -R && chown $NB_USER $CAFFE_ROOT -R
USER $NB_USER

ARG UNTRIMMED_CLONE_TAG=master
RUN git clone -b ${UNTRIMMED_CLONE_TAG} --depth 1 https://github.com/TMRert/UntrimmedNet.git .
RUN sed -i 's#http://mcg.nju.edu.cn/models/UntrimmedNet/#https://www.dropbox.com/sh/8yxjj4fbgm2omjd/AADA_ebg-pciLSoC6dUoT1cwa?preview=#g' scripts/get_reference_model_anet.sh
RUN scripts/get_reference_model_anet.sh

RUN conda install jupyter pyparsing
RUN conda update -y --all
RUN conda clean -yt

USER root
RUN apt-get update && apt-get install -y --no-install-recommends nano
USER $NB_USER
