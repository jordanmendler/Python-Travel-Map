#!/bin/bash - 
#===============================================================================
#
#          FILE: clean_up_google_photos.sh
# 
#         USAGE: ./clean_up_google_photos.sh 
# 
#   DESCRIPTION: 
# 
#        AUTHOR: YOUR NAME (), 
#       CREATED: 08/30/2019 15:39
#      REVISION:  ---
#===============================================================================

DIR="~/Downloads/Takeout/Google Photos"

# Remove all media files
for filetype in mp4 jpg mov png gif ; do
    find "$DIR" -type filetype -iname *.$i -exec rm -f "{}" \; ;
done

# Remove all empty directories
find "$DIR" -type d -exec rmdir "{}" \;

# FIXME: Combine all JSON metadata to compile locations
