#!/bin/bash

csv_dir=shifts_by_month
posts_dir=_posts

DATE=`date +%Y-%m-%d`

for file in `ls ./shift_by_month`; do
    base=`echo $file | cut -c1-7`
    echo $base
    md_file=$DATE-$base.markdown
    YEAR=`echo $base | cut -c1-4`
    MONTH=`echo $base | cut -c6-7`
    echo "---" > $posts_dir/$md_file
    echo "title: Citizen Science ${MONTH}-${YEAR}" >> $posts_dir/$md_file
    echo "owner: WOEIP" >> $posts_dir/$md_file
    echo "layout: data" >> $posts_dir/$md_file
    echo "month: ${MONTH}" >> $posts_dir/$md_file
    echo "year: ${YEAR}" >> $posts_dir/$md_file
    echo "categories: citizenScience" >> $posts_dir/$md_file
    echo "fileName: <a href=\"http://s3-us-west-2.amazonaws.com/openoakland-woaq/shift_by_month/$file\">CSV here</a>" \
        >> $posts_dir/$md_file
    echo "---" >> $posts_dir/$md_file

done
