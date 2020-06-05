import json
import os.path as osp
import glob

class Config():

    def __init__(self, config):
        assert osp.exists(config)

        with open(config, "r") as fp:
            for key, val in json.load(fp).items():
                setattr(self, key, val)
        self.fnames = glob.glob('data/*.png')