#!/bin/bash

sudo docker build -t dlcapp .
sudo docker run -p 8050:8050 \
    --mount type=bind,source=$(pwd)/data,destination=/app/data,readonly \
    --user nobody -it dlcapp