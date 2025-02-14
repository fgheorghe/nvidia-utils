FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y software-properties-common &&  apt-get install -y htop wget curl mc git nvtop bpytop btop 


COPY code /code

WORKDIR /code

RUN python3 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# CMD . venv/bin/activate && streamlit run nvidia.py
CMD /usr/local/bin/entrypoint.sh
