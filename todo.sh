#!/bin/sh

for f in $(find tchess bin -type f -name '*.py') test.py bin/tchess; do
	TODOs=$(cat $f | grep 'TODO')
	if [ "$TODOs" != "" ]
	then
		echo $f:
		cat $f | grep 'TODO'
		echo '--------------'
	fi
done
