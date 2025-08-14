import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Tesla 3D Component Viewer")

# ----------------------------
# Tesla component data
# ----------------------------
tesla_data = {
    "Cybertruck": {
        "coords": {
            "BCM": [0, 0.5, 0.2], "FSD ECU": [0.5, 0.5, 0.2],
            "Security Horn": [-0.8, 1.2, 0.3], "Hazard Lights Front": [0, 1.5, 0.7],
            "Hazard Lights Rear": [0, -1.5, 0.7], "Front Fascia Camera": [0, 1.5, 0.8],
            "Left Fender Camera": [-0.6, 1.2, 0.9], "Right Fender Camera": [0.6, 1.2, 0.9],
            "Left B-Pillar Camera": [-0.6, 0, 1.0], "Right B-Pillar Camera": [0.6, 0, 1.0],
            "Rear Camera": [0, -1.6, 0.8]
        },
        "connections": [
            ["Security Horn", "BCM"], ["Hazard Lights Front", "BCM"], ["Hazard Lights Rear", "BCM"],
            ["Front Fascia Camera", "FSD ECU"], ["Left Fender Camera", "FSD ECU"], ["Right Fender Camera", "FSD ECU"],
            ["Left B-Pillar Camera", "FSD ECU"], ["Right B-Pillar Camera", "FSD ECU"], ["Rear Camera", "FSD ECU"]
        ]
    },
    "Model 3": {
        "coords": {
            "BCM": [0, 0.45, 0.2], "FSD ECU": [0.5, 0.45, 0.2],
            "Security Horn": [-0.75, 1.15, 0.35], "Hazard Lights Front": [0, 1.45, 0.7],
            "Hazard Lights Rear": [0, -1.45, 0.7], "Front Fascia Camera": [0, 1.45, 0.85],
            "Left Fender Camera": [-0.6, 1.1, 0.9], "Right Fender Camera": [0.6, 1.1, 0.9],
            "Left B-Pillar Camera": [-0.6, 0, 1.0], "Right B-Pillar Camera": [0.6, 0, 1.0],
            "Rear Camera": [0, -1.55, 0.8], "Radar Sensor": [0, 1.3, 0.25], "Charge Port ECU": [-0.65, -1.4, 0.65]
        },
        "connections": [
            ["Security Horn", "BCM"], ["Hazard Lights Front", "BCM"], ["Hazard Lights Rear", "BCM"],
            ["Front Fascia Camera", "FSD ECU"], ["Left Fender Camera", "FSD ECU"], ["Right Fender Camera", "FSD ECU"],
            ["Left B-Pillar Camera", "FSD ECU"], ["Right B-Pillar Camera", "FSD ECU"], ["Rear Camera", "FSD ECU"],
            ["Radar Sensor", "FSD ECU"], ["Charge Port ECU", "BCM"]
        ]
    },
    "Model S": {
        "coords": {
            "BCM": [0, 0.5, 0.25], "FSD ECU": [0.55, 0.5, 0.25],
            "Security Horn": [-0.8, 1.2, 0.35], "Hazard Lights Front": [0, 1.55, 0.75],
            "Hazard Lights Rear": [0, -1.55, 0.75], "Front Fascia Camera": [0, 1.55, 0.85],
            "Left Fender Camera": [-0.65, 1.25, 0.95], "Right Fender Camera": [0.65, 1.25, 0.95],
            "Left B-Pillar Camera": [-0.65, 0, 1.05], "Right B-Pillar Camera": [0.65, 0, 1.05],
            "Rear Camera": [0, -1.6, 0.85], "Radar Sensor": [0, 1.35, 0.3], "Charge Port ECU": [-0.7, -1.45, 0.7]
        },
        "connections": [
            ["Security Horn", "BCM"], ["Hazard Lights Front", "BCM"], ["Hazard Lights Rear", "BCM"],
            ["Front Fascia Camera", "FSD ECU"], ["Left Fender Camera", "FSD ECU"], ["Right Fender Camera", "FSD ECU"],
            ["Left B-Pillar Camera", "FSD ECU"], ["Right B-Pillar Camera", "FSD ECU"], ["Rear Camera", "FSD ECU"],
            ["Radar Sensor", "FSD ECU"], ["Charge Port ECU", "BCM"]
        ]
    },
    "Model X": {
        "coords": {
            "BCM": [0, 0.55, 0.25], "FSD ECU": [0.6, 0.55, 0.25],
            "Security Horn": [-0.85, 1.25, 0.35], "Hazard Lights Front": [0, 1.6, 0.8],
            "Hazard Lights Rear": [0, -1.6, 0.8], "Front Fascia Camera": [0, 1.6, 0.9],
            "Left Fender Camera": [-0.7, 1.3, 1.0], "Right Fender Camera": [0.7, 1.3, 1.0],
            "Left B-Pillar Camera": [-0.7, 0, 1.1], "Right B-Pillar Camera": [0.7, 0, 1.1],
            "Rear Camera": [0, -1.65, 0.9], "Radar Sensor": [0, 1.4, 0.35], "Charge Port ECU": [-0.75, -1.5, 0.75]
        },
        "connections": [
            ["Security Horn", "BCM"], ["Hazard Lights Front", "BCM"], ["Hazard Lights Rear", "BCM"],
            ["Front Fascia Camera", "FSD ECU"], ["Left Fender Camera", "FSD ECU"], ["Right Fender Camera", "FSD ECU"],
            ["Left B-Pillar Camera", "FSD ECU"], ["Right B-Pillar Camera", "FSD ECU"], ["Rear Camera", "FSD ECU"],
            ["Radar Sensor", "FSD ECU"], ["Charge Port ECU", "BCM"]
        ]
    },
    "Model Y": {
        "coords": {
            "BCM": [0, 0.45, 0.25], "FSD ECU": [0.5, 0.45, 0.25],
            "Security Horn": [-0.75, 1.15, 0.35], "Hazard Lights Front": [0, 1.5, 0.75],
            "Hazard Lights Rear": [0, -1.5, 0.75], "Front Fascia Camera": [0, 1.5, 0.85],
            "Left Fender Camera": [-0.6, 1.2, 0.95], "Right Fender Camera": [0.6, 1.2, 0.95],
            "Left B-Pillar Camera": [-0.6, 0, 1.05], "Right B-Pillar Camera": [0.6, 0, 1.05],
            "Rear Camera": [0, -1.55, 0.85], "Radar Sensor": [0, 1.3, 0.3], "Charge Port ECU": [-0.65, -1.4, 0.7]
        },
        "connections": [
            ["Security Horn", "BCM"], ["Hazard Lights Front", "BCM"], ["Hazard Lights Rear", "BCM"],
            ["Front Fascia Camera", "FSD ECU"], ["Left Fender Camera", "FSD ECU"], ["Right Fender Camera", "FSD ECU"],
            ["Left B-Pillar Camera", "FSD ECU"], ["Right B-Pillar Camera", "FSD ECU"], ["Rear Camera", "FSD ECU"],
            ["Radar Sensor", "FSD ECU"], ["Charge Port ECU", "BCM"]
        ]
    }
}

# ----------------------------
# Model selection
# ----------------------------
model = st.selectbox("Select Tesla model", list(tesla_data.keys()))
coords = tesla_data[model]["coords"]
connections = tesla_data[model]["connections"]

# ----------------------------
# Build Plotly traces
# ----------------------------
traces = []

# Component points
for name, pos in coords.items():
    traces.append(go.Scatter3d(
        x=[pos[0]], y=[pos[1]], z=[pos[2]],
        mode='markers+text',
        marker=dict(size=6, color='cyan'),
        text=[name],
        textposition='top center',
        name=name
    ))

# Connections
for a, b in connections:
    traces.append(go.Scatter3d(
        x=[coords[a][0], coords[b][0]],
        y=[coords[a][1], coords[b][1]],
        z=[coords[a][2], coords[b][2]],
        mode='lines',
        line=dict(color='orange', width=3),
        name=f"{a}-{b}"
    ))

# Car mesh (semi-transparent)
import numpy as np

# Compute bounding box for component coordinates
all_coords = np.array(list(coords.values()))
min_x, min_y, min_z = all_coords.min(axis=0) - 0.3
max_x, max_y, max_z = all_coords.max(axis=0) + 0.3

# Build simple rectangular mesh around features
meshX = [min_x, max_x, max_x, min_x, min_x, max_x, max_x, min_x]
meshY = [min_y, min_y, max_y, max_y, min_y, min_y, max_y, max_y]
meshZ = [min_z, min_z, min_z, min_z, max_z, max_z, max_z, max_z]

# Triangles for the cube
i = [0,0,0,4,4,1,2,3,5,6,1,2]
j = [1,2,3,5,6,5,6,7,6,7,2,3]
k = [2,3,0,6,7,6,7,4,7,4,3,0]

traces.append(go.Mesh3d(
    x=meshX, y=meshY, z=meshZ,
    i=i, j=j, k=k,
    color='lightgrey',
    opacity=0.15,
    flatshading=True,
    name="Car Body"
))

# ----------------------------
# Layout
# ----------------------------
layout = go.Layout(
    scene=dict(
        xaxis=dict(title='Width (L-R)'),
        yaxis=dict(title='Length (F-B)'),
        zaxis=dict(title='Height'),
        aspectmode='manual',
        aspectratio=dict(x=1.5, y=3, z=1)
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    title=f"{model} - 3D Component Map"
)

fig = go.Figure(data=traces, layout=layout)

st.plotly_chart(fig, use_container_width=True)
