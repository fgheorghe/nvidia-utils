FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y htop wget curl mc git nvtop bpytop btop glances 

RUN apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip pipx

RUN pip install git+https://github.com/leftthomas/GPUView.git@master

CMD gpuview run --host 0.0.0.0

