#!/bin/bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python3 main.py $1
epstopdf 1.eps -o 1.pdf
convert 1.pdf -channel RGB -negate $1$(date +%y%m%d).png
rm 1.pdf 1.eps
