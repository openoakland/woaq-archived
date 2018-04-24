#!/bin/bash

echo "setting up _posts directory..."

if [ -d "./_posts" ]; then
    rm -rf ./_posts
fi
mkdir _posts

for filename in ./shifts/*.csv; do
    post_output=./_posts/${f%.*}.markdown
    yml_src=./yml_template/${f%.*}.yml

    if [ ! -f yml_src ]; then
        echo "$yml_src not defined"
        exit 1
    fi

    # yaml front matter
    echo "---" > post_output
    cat yml_src >> post_output
    echo "---" >> post_output

    cat _layouts/data.html >> post_output
done
echo "done"
