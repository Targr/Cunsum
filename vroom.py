import streamlit as st
import plotly.graph_objects as go

# --- Component coordinates (top view only) ---
tesla_data = {
    "Cybertruck": {
        "coords": {
            "BCM": [0, 0.5], "FSD ECU": [0.5, 0.5], "Security Horn": [-0.8, 1.2],
            "Hazard Lights Front": [0, 1.5], "Hazard Lights Rear": [0, -1.5],
            "Front Fascia Camera": [0, 1.5], "Left Fender Camera": [-0.6, 1.2],
            "Right Fender Camera": [0.6, 1.2], "Left B-Pillar Camera": [-0.6, 0],
            "Right B-Pillar Camera": [0.6, 0], "Rear Camera": [0, -1.6]
        }
    },
    "Model 3": {
        "coords": {
            "BCM": [0, 0.45], "FSD ECU": [0.5, 0.45], "Security Horn": [-0.75, 1.15],
            "Hazard Lights Front": [0, 1.45], "Hazard Lights Rear": [0, -1.45],
            "Front Fascia Camera": [0, 1.45], "Left Fender Camera": [-0.6, 1.1],
            "Right Fender Camera": [0.6, 1.1], "Left B-Pillar Camera": [-0.6, 0],
            "Right B-Pillar Camera": [0.6, 0], "Rear Camera": [0, -1.55],
            "Radar Sensor": [0, 1.3], "Charge Port ECU": [-0.65, -1.4]
        }
    },
    "Model S": {
        "coords": {
            "BCM": [0, 0.5], "FSD ECU": [0.55, 0.5], "Security Horn": [-0.8, 1.2],
            "Hazard Lights Front": [0, 1.55], "Hazard Lights Rear": [0, -1.55],
            "Front Fascia Camera": [0, 1.55], "Left Fender Camera": [-0.65, 1.25],
            "Right Fender Camera": [0.65, 1.25], "Left B-Pillar Camera": [-0.65, 0],
            "Right B-Pillar Camera": [0.65, 0], "Rear Camera": [0, -1.6],
            "Radar Sensor": [0, 1.35], "Charge Port ECU": [-0.7, -1.45]
        }
    },
    "Model X": {
        "coords": {
            "BCM": [0, 0.55], "FSD ECU": [0.6, 0.55], "Security Horn": [-0.85, 1.25],
            "Hazard Lights Front": [0, 1.6], "Hazard Lights Rear": [0, -1.6],
            "Front Fascia Camera": [0, 1.6], "Left Fender Camera": [-0.7, 1.3],
            "Right Fender Camera": [0.7, 1.3], "Left B-Pillar Camera": [-0.7, 0],
            "Right B-Pillar Camera": [0.7, 0], "Rear Camera": [0, -1.65],
            "Radar Sensor": [0, 1.4], "Charge Port ECU": [-0.75, -1.5]
        }
    },
    "Model Y": {
        "coords": {
            "BCM": [0, 0.45], "FSD ECU": [0.5, 0.45], "Security Horn": [-0.75, 1.15],
            "Hazard Lights Front": [0, 1.5], "Hazard Lights Rear": [0, -1.5],
            "Front Fascia Camera": [0, 1.5], "Left Fender Camera": [-0.6, 1.2],
            "Right Fender Camera": [0.6, 1.2], "Left B-Pillar Camera": [-0.6, 0],
            "Right B-Pillar Camera": [0.6, 0], "Rear Camera": [0, -1.55],
            "Radar Sensor": [0, 1.3], "Charge Port ECU": [-0.65, -1.4]
        }
    },
}

st.title("Tesla Component Viewer (Top View)")

model = st.selectbox("Choose a Tesla model", list(tesla_data.keys()))
coords = tesla_data[model]["coords"]

fig = go.Figure()

# Add components as points
for name, (x, y) in coords.items():
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode="markers+text",
        text=[name],
        textposition="top center",
        marker=dict(size=10, color="cyan")
    ))

fig.update_layout(
    xaxis=dict(title="Width (L-R)"),
    yaxis=dict(title="Length (F-B)", scaleanchor="x"),
    width=700,
    height=900,
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig, use_container_width=True)
