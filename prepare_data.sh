#!/bin/bash

mkdir -p data
parallel wget :::: config/filelist.lst
mv *.png data
