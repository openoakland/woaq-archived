#!/bin/bash

csv_dir=shifts_by_month
posts_dir=_posts

DATE=`date +%Y-%m-%d`

# Make a separate page for each file in.
for file in `ls ./shift_by_month`; do
    base=`echo $file | cut -c1-7`
    echo $base
    md_file=$posts_dir/$DATE-$base.markdown
    YEAR=`echo $base | cut -c1-4`
    MONTH=`echo $base | cut -c6-7`

    # Write yaml file line by line
    cat <<EOF  >$md_file
---
title: WOEIP Air Quality ${MONTH}-${YEAR}
owner: <a href="https://www.woeip.org/">WOEIP</a>
layout: data
month: ${MONTH}
year: ${YEAR}
categories: WOEIP
resourceType: shift_by_month
fileName: $file
---
EOF

done
