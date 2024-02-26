#!/bin/bash
pip3 install playwright
# echo "export PATH=\$PATH:/home/ubuntu/.local/bin"
PLAYWRIGHT=~/.local/bin/playwright
$PLAYWRIGHT install
$PLAYWRIGHT install-deps
