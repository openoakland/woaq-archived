#!/bin/bash

mkdir -p shift_by_month

# OK i know this is hacky, but bear with me.
# This is the state of our world right now.
# The time readings within each data set are
# only avaiable via UTC time stamps. 
# I'm not good enough with SQL to figure out how to
# get the sql query to automatically extract months for us.
# So we just cut out the relevant characters from the names of 
# the file and use that to match files from the same dates.
for pref in `ls shifts  | cut -c4-10 | sort | uniq`; do

    # We want to print the CSV header only once.
    skip_line=0
    rm -f shift_by_month/$pref.csv
    for file in `ls shifts/*$pref*`; do
        tail -n +$skip_line $file >> shift_by_month/$pref.csv
        skip_line=2
    done
    echo $pref
done

