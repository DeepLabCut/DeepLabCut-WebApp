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
import time

import pandas as pd

import custom_types

class User():
    """ Each user has a separate view on the labels and can label each image once """

    def __init__(self, name):
        self.name = name

    def add_annotation(self):
        pass

    def to_csv(self):
        return None

class Dataset():
    """ Handles async data fetching """

    def __init__(self, fnames):
        self.fnames = fnames

    def __getitem__(self, index):
        if index >= len(self):
            raise StopIteration

        fname = self.fnames[index]
        img = io.imread(fname)
        img = img[::5,::5]
        return custom_types.image(fname = fname, image = img)

    def __len__(self):
        return len(self.fnames)

class AppModel():

    def __init__(self, config):
        
        self.config = config
        self.users = []
        self.dataset = Dataset(self.config.fnames)
        self.annotations = []
        self.active_image = None

    def add_user(self, name):
        print(f"| Added user: {name}")
        self.users.append(User(name))

    def add_annotation(self, name, username, xy):
        self.annotations.append(dict(
            name = self.active_image.fname,
            x = xy[0],
            y = xy[1],
            username = username,
            timestamp = time.time())
        )

    def fetch_image(self, index):
        self.active_image = self.dataset[index]
        return  self.active_image

    def to_csv(self):
        return pd.DataFrame(self.annotations).to_csv()

    def to_html(self):
        return pd.DataFrame(self.annotations).to_html()