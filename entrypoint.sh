#!/bin/bash
set -e

nohup /usr/bin/glances -w &

. venv/bin/activate && streamlit run nvidia.py

