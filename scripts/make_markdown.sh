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
    echo "---" > $md_file
    echo "title: Citizen Science ${MONTH}-${YEAR}" >> $md_file
    echo "owner: WOEIP" >> $md_file
    echo "layout: data" >> $md_file
    echo "month: ${MONTH}" >> $md_file
    echo "year: ${YEAR}" >> $md_file
    echo "categories: citizenScience" >> $md_file
    echo "fileName: <a href=\"http://s3-us-west-2.amazonaws.com/openoakland-woaq/shift_by_month/$file\">CSV here</a>" \
        >> $md_file
    echo "---" >> $md_file

done
