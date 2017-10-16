#!/bin/bash
while :
do
    # TASK 1
    date
    read -t 100 -n 1 key

    if [[ $key = q ]]
    then
        break
    fi
done

# TASK 2
date +%s
