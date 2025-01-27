import streamlit as st
import pynvml
import time
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from collections import deque

# Initialize NVML
pynvml.nvmlInit()

# Set page config
st.set_page_config(
    page_title="GPU Monitor",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("Real-time GPU Monitoring Dashboard")

# Initialize session state for storing historical data
if 'gpu_data' not in st.session_state:
    st.session_state.gpu_data = {
        'timestamp': deque(maxlen=600),  # 10 minutes * 60 seconds
        'memory_used': {},
        'utilization': {},
        'temperature': {},
        'power_usage': {}
    }

# Get number of GPUs
device_count = pynvml.nvmlDeviceGetCount()

# Initialize deques for each GPU if not already done
for i in range(device_count):
    if i not in st.session_state.gpu_data['memory_used']:
        st.session_state.gpu_data['memory_used'][i] = deque(maxlen=600)
        st.session_state.gpu_data['utilization'][i] = deque(maxlen=600)
        st.session_state.gpu_data['temperature'][i] = deque(maxlen=600)
        st.session_state.gpu_data['power_usage'][i] = deque(maxlen=600)


def get_gpu_metrics():
    """Get current GPU metrics for all GPUs"""
    metrics = []
    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)

        # Get memory info
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        memory_used = memory.used / 1024 ** 2  # Convert to MB

        # Get utilization info
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_util = utilization.gpu

        # Get temperature
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

        # Get power usage
        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # Convert to Watts

        metrics.append({
            'memory_used': memory_used,
            'utilization': gpu_util,
            'temperature': temp,
            'power_usage': power
        })
    return metrics


def update_data():
    """Update the GPU data in session state"""
    current_time = datetime.now()
    st.session_state.gpu_data['timestamp'].append(current_time)

    metrics = get_gpu_metrics()
    for i, gpu_metrics in enumerate(metrics):
        st.session_state.gpu_data['memory_used'][i].append(gpu_metrics['memory_used'])
        st.session_state.gpu_data['utilization'][i].append(gpu_metrics['utilization'])
        st.session_state.gpu_data['temperature'][i].append(gpu_metrics['temperature'])
        st.session_state.gpu_data['power_usage'][i].append(gpu_metrics['power_usage'])


def create_plot(metric_name, ylabel, data_dict):
    """Create a plotly figure for the given metric"""
    fig = go.Figure()

    # Calculate max value based on metric type
    max_value = max(max(list(data)) if list(data) else 0 for data in data_dict.values())

    # Add padding and set defaults based on metric type
    if metric_name == 'Temperature':
        max_value = max_value * 1.1 if max_value > 0 else 100
    elif metric_name == 'Utilization':
        max_value = 100  # GPU utilization is always 0-100%
    elif metric_name == 'Memory Usage':
        max_value = max_value * 1.1 if max_value > 0 else 1000  # Default to 1000MB if no data
    elif metric_name == 'Power Usage':
        max_value = max_value * 1.1 if max_value > 0 else 300  # Default to 300W if no data

    for gpu_id in range(device_count):
        fig.add_trace(go.Scatter(
            x=list(st.session_state.gpu_data['timestamp']),
            y=list(data_dict[gpu_id]),
            name=f'GPU {gpu_id}',
            mode='lines'
        ))

    layout_dict = {
        'title': f'GPU {metric_name} Over Time',
        'xaxis_title': 'Time',
        'yaxis_title': ylabel,
        'height': 300,
        'margin': dict(l=0, r=0, t=40, b=0),
        'yaxis': dict(range=[0, max_value])
    }

    fig.update_layout(**layout_dict)
    return fig


# Create layout
col1, col2 = st.columns(2)

# Placeholder for plots
memory_plot = col1.empty()
util_plot = col1.empty()
temp_plot = col2.empty()
power_plot = col2.empty()

# Main loop
try:
    while True:
        update_data()

        # Update plots
        memory_plot.plotly_chart(
            create_plot('Memory Usage', 'Memory (MB)', st.session_state.gpu_data['memory_used']),
            use_container_width=True
        )

        util_plot.plotly_chart(
            create_plot('Utilization', 'Utilization (%)', st.session_state.gpu_data['utilization']),
            use_container_width=True
        )

        temp_plot.plotly_chart(
            create_plot('Temperature', 'Temperature (°C)', st.session_state.gpu_data['temperature']),
            use_container_width=True
        )

        power_plot.plotly_chart(
            create_plot('Power Usage', 'Power (W)', st.session_state.gpu_data['power_usage']),
            use_container_width=True
        )

        time.sleep(1)  # Update every second

except KeyboardInterrupt:
    # Clean up NVML
    pynvml.nvmlShutdown()

# Cleanup on exit
