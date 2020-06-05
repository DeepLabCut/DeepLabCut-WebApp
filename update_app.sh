#!/bin/bash

# check github and update app if needed
# run with watch

update=$(git fetch --dry-run |& grep stes/webinar | wc -l)
if [[ $update -ne 0 ]]; then
    git pull origin stes/webinar
fi

