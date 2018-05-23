#!/bin/bash

mkdir -p shift_by_month

rm -rf shift_by_month/*

for pref in `ls shifts  | cut -c4-10 | sort | uniq`; do
    # We want the header from the first CSV, but not the remaining ones
    skip_line=0
    for file in `ls shifts/*$pref*`; do
        tail -n +$skip_line $file >> shift_by_month/$pref
        skip_line=2
    done
    echo $pref
done

# this is terrible, i know.
cd shift_by_month

for file in *; do
    mv -- "$file" "${file//[/}.csv"
done

