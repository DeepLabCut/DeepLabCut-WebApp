import flask

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import json
import os
import matplotlib.cm
import matplotlib.colors as mcolors
import numpy as np
import random
import plotly.graph_objects as go
import plotly.express as px
from skimage import data, transform, io
import numpy as np
import glob
import json

def draw_circle(center, radius, n_points=50):
    pts = np.linspace(0, 2 * np.pi, n_points)
    x = center[0] + radius * np.cos(pts)
    y = center[1] + radius * np.sin(pts)
    path = 'M ' + str(x[0]) + ',' + str(y[1])
    for k in range(1, x.shape[0]):
        path += ' L ' + str(x[k]) + ',' + str(y[k])
    path += ' Z'
    return path


def compute_circle_center(path):
    """
    See Eqn 1 & 2 pp.12-13 in REGRESSIONS CONIQUES, QUADRIQUES
    Régressions linéaires et apparentées, circulaire, sphérique
    Jacquelin J., 2009.
    """
    coords = [list(map(float, coords.split(','))) for coords in path.split(' ')[1::2]]
    x, y = np.array(coords).T
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_x2 = np.sum(x * x)
    sum_y2 = np.sum(y * y)
    delta11 = n * np.dot(x, y) - sum_x * sum_y
    delta20 = n * sum_x2 - sum_x ** 2
    delta02 = n * sum_y2 - sum_y ** 2
    delta30 = n * np.sum(x ** 3) - sum_x2 * sum_x
    delta03 = n * np.sum(y ** 3) - sum_y * sum_y2
    delta21 = n * np.sum(x * x * y) - sum_x2 * sum_y
    delta12 = n * np.sum(x * y * y) - sum_x * sum_y2

    # Eqn 2, p.13
    num_a = (delta30 + delta12) * delta02 - (delta03 + delta21) * delta11
    num_b = (delta03 + delta21) * delta20 - (delta30 + delta12) * delta11
    den = 2 * (delta20 * delta02 - delta11 * delta11)
    a = num_a / den
    b = num_b / den
    return a, b

def get_plotly_color(cmap, n):
    return mcolors.to_hex(cmap(n))