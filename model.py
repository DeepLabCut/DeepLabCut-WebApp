from skimage import io
import time

import pandas as pd

import custom_types


class User:
    """ Each user has a separate view on the labels and can label each image once """

    def __init__(self, name):
        self.name = name

    def add_annotation(self):
        pass

    def to_csv(self):
        return None


class Dataset:
    """ Handles async data fetching """

    def __init__(self, fnames):
        self.fnames = fnames

    def __getitem__(self, index):
        if index >= len(self):
            raise StopIteration

        fname = self.fnames[index]
        img = io.imread(fname)
        # TODO revert this at some point
        img = img[::5, ::5]
        return custom_types.Image(fname=fname, image=img)

    def __len__(self):
        return len(self.fnames)


class AppModel:

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
            name=self.active_image.fname,
            label=name,
            x=xy[0],
            y=xy[1],
            username=username,
            timestamp=time.time())
        )

    def fetch_image(self, index):
        self.active_image = self.dataset[index]
        return self.active_image

    def to_csv(self):
        return pd.DataFrame(self.annotations).to_csv()

    def to_html(self):
        return pd.DataFrame(self.annotations).to_html()