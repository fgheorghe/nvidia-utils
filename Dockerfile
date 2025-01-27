FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y htop wget curl mc git nvtop bpytop btop glances 
RUN sh -c 'wget -O - https://github.com/nicolargo/glances/archive/refs/tags/v$(glances -V|cut -zd" " -f2|tr -d v).tar.gz | tar -xz -C /usr/lib/python3/dist-packages/glances/outputs/static/ --strip-components=4 --wildcards glances-*/glances/outputs/static/public/'
RUN apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip pipx 

COPY code /code

WORKDIR /code

RUN python3.10 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# CMD . venv/bin/activate && streamlit run nvidia.py
CMD /usr/local/bin/entrypoint.sh
