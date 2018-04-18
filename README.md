To install on Mac:

## Grab the source
git clone -b gh-pages --single-branch  https://github.com/openoakland/woaq.git

## Install jekyll locally
bundle install

## Fire up the local server
jekyll serve

## View the site
Open a browser and navigate to: http://127.0.0.1:4000/woaq/

## Jekyll data post convention
Save your Jekyll data post files in the following format:
* Filename convention: "YYYY-MM-DD-full_name.markdown"
* At top of file, include your front matter:
  * "---" 
  * "title: [post title]"
  * "location: [file location in google drive]"
  * "fileName: [file name]"
  * "layout: post" (keep this standard)
  * "categories: [post_category_1 post_category_2]"
  * "---"
* Then include your post content (TBD)
