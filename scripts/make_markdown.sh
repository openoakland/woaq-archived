#!/bin/bash

csv_dir=shifts_by_month
posts_dir=_posts

DATE=`date +%Y-%m-%d`

for file in `ls shifts_by_month`; do
    base=`echo file | cut -c1-9`
    md_file=$DATE-$base.markdown
    echo "---" > $posts_dir/$md_file
    echo "categories: citizenScience" >> $posts_dir/$md_file
    echo "URL: http://s3-us-west-2.amazonaws.com/openoakland-woaq/shift_by_month/$file" \
        >>$posts_dir/$md_file
    echo "---" >> $posts_dir/$md_file
    

done
