#!/bin/bash
pip3 install playwright
echo "export PATH=\$PATH:/home/ubuntu/.local/bin"
playwright install
playwright install-deps
