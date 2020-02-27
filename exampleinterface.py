#interface to dlc

import deeplabcut, os
import pandas as pd
from pathlib import Path

cfgpath='/home/alex/Hacking/DeepLabCut-WebApp/openfield-Pranav-2018-10-30/config.yaml'
deeplabcut.create_project.demo_data.load_demo_data(cfgpath,createtrainingset=False)


cfg = deeplabcut.auxiliaryfunctions.read_config(cfgpath)


videos = cfg['video_sets'].keys()
#video_names = [Path(i).stem for i in videos]
alldatafolders = [fn for fn in os.listdir(Path(cfgpath).parent / 'labeled-data') if '_labeled' not in fn]

print("Bodyparts to label...", cfg['bodyparts'])
print("Labeled-data contains:", len(alldatafolders))

datafolder=alldatafolders[0]
#loading data
dataFrame = pd.read_hdf(os.path.join(cfg['project_path'],'labeled-data',datafolder,'CollectedData_'+cfg['scorer']+'.h5'),'df_with_missing')
print(dataFrame.head())
