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

DIR=~/Downloads/Takeout/Google\ Photos/

# Remove all media files
for filetype in heic mp4 jpg jpeg mov png gif ; do
    find "$DIR" -type f -iname \*.$filetype -exec rm -f "{}" \;
done

# Remove all empty directories
find "$DIR" -type d -empty -delete

# FIXME: Combine all JSON metadata to compile locations
