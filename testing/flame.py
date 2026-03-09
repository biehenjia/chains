import plotly.graph_objects as go
import numpy as np

def plot_surfaces(*arrays):
    fig = go.Figure()

    for z in arrays:
        z = np.array(z)
        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])

        fig.add_surface(x=x, y=y, z=z)

    fig.show()