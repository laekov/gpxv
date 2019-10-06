#!/bin/bash
if [ $2. = . ]
then
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python3 main.py $1
	mv combined.png $1$(date +%y%m%d).png
else
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python3 main.py $1 $2
	mv combined.png comb$(date +%y%m%d).png
fi
