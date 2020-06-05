#!/bin/bash
# Generates a file list of possible images

wget --spider -r --no-parent http://deeplabcut.rowland.harvard.edu/datasets/ \
|& grep http \
| grep png \
| awk '{print $3}'
