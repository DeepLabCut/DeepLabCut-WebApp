#!/bin/bash

sudo docker build -t dlcapp .
sudo docker run -p 8050:8050 --user nobody -it dlcapp