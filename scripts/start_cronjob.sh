#!/bin/bash

nohup python3 ./cronjob.py > nohup.out 2> nohup.err < /dev/null &