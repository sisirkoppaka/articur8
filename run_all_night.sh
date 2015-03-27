#!/bin/bash

# This runs fd every 10 mins

i=1

while true; do
	echo "Iteration "$i
	sh stuff.sh
	((i++))
	sleep 600 # stupid mac doesn't take minutes
done