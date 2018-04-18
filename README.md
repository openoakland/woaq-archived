## To install on Mac:

### Grab the source
git clone -b gh-pages --single-branch  https://github.com/openoakland/woaq.git

### Install jekyll locally
bundle install

### Fire up the local server
jekyll serve

### View the site
Open a browser and navigate to: http://127.0.0.1:4000/woaq/

## Jekyll data post convention
Save your Jekyll data post files in the following format (refer to post dir for examples):

* Filename convention: "YYYY-MM-DD-full_name.markdown"
* At top of file, include your front matter:
  * "---" 
  * "title: post_title"
  * "location: file_location_in_google_drive"
  * "fileName: file_name"
  * "layout: post" (keep this standard)
  * "categories: post_category_1 post_category_2"
  * "---"
* Then include your post content (TBD)

## Jekyll Site Information

Post styling on individual data pages (e.g. https://openoakland.github.io/woaq/transportation/2018/04/17/prohibited_truck_routes_edf_spatial.html) is handled by the file in _layouts/data 
