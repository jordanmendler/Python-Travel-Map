#!/usr/bin/python3

import re
import json
import os
import tempfile
import shutil
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import plotly as py
import math
import csv
import sys

# Make sure input file was specified
if len(sys.argv) < 2:
    print("Please specify input file")
    print("Example: ./travel_map_plot.py Travel_Map_All.csv ")
    sys.exit(1)


# Functions


def validCoords(lat, lng):
    if lat < 85 and lat > -60 and lng <= 180 and lng >= -180:
        return True
    else:
        return False


# Split sorted files into smaller files with no more than 10000 lines each
lines_per_file = 10000

# Make a cache directory
tmp_dir = str(tempfile.mkdtemp())

# Clean and merge input files
files = sys.argv
files.pop(0)

with open(tmp_dir + "/Travel_Map_Cleaned.csv", mode="w") as outfile:
    writeCSV = csv.writer(outfile, delimiter=",")

    for f in files:
        print("Processing " + f)
        with open(f) as infile:
            count = 0
            skipped = 0
            if ".csv" in f:
                readCSV = csv.reader(infile, delimiter=",")
                for row in readCSV:
                    try:
                        lat = float(row[0])
                        lng = float(row[1])

                        if validCoords(lat, lng):
                            writeCSV.writerow([lat, lng])
                            count += 1
                    except ValueError:
                        skipped += 1
                        # print("\tSkipped:, "lat", ",", lng)
                        pass

            elif ".json" in f:
                # FIXME: Support JSON input
                print("JSON not yet supported")
                sys.exit(1)

            elif ".kml" in f:
                regex = "<gx:coord>([+-]?\d+?\.\d+) ([+-]?\d+?\.\d+) 0</gx:coord>"
                for line in infile:
                    for match in re.findall(regex, line):
                        try:
                            lng = float(match[0])
                            lat = float(match[1])

                            if validCoords(lat, lng):
                                count += 1
                                writeCSV.writerow([lat, lng])
                        except ValueError:
                            skipped += 1
                            # print("\tSkipped:, "lat", ",", lng)
                            pass
            else:
                print(
                    "Please only in .csv or .json files. Unrecognized filetype for " + f
                )
                sys.exit(1)
            print("\tSkipped ", skipped)
            print("\tProcessed ", count)


# Sort points
# FIXME: This can be merged with prior step
os.system(
    "sort "
    + tmp_dir
    + "/Travel_Map_Cleaned.csv | uniq > "
    + tmp_dir
    + "/Travel_Map_Sorted.csv"
)

# Split into multiple files
newfile = None
file_num = 0
my_files = []
with open(tmp_dir + "/Travel_Map_Sorted.csv") as infile:
    for lineno, line in enumerate(infile, -1):
        if lineno >= 0:
            if lineno % lines_per_file == 0:
                if newfile:
                    newfile.close()
                file_num = lineno // lines_per_file + 1
                new_filename = tmp_dir + "/Travel_Map_p{}.csv".format(file_num)
                my_files.append(new_filename)
                newfile = open(new_filename, "w")
            newfile.write(line)


# Trim points by density(distance between two closest points)
countOrig = 0
count = 0
coordinates = []

for filename in my_files:
    coords = []
    with open(filename) as infile:
        for row in infile:
            row = row.strip().split(",")
            new_point = (float(row[0]), float(row[1]))

            add = True
            if coords == None:
                coords.append(new_point)
                count += 1
                print(count, "added:", new_point)
            else:
                for j in range(len(coords) - 1, -1, -1):
                    # FIXME: This should be moved into a function
                    lat1 = new_point[0]
                    lat0 = coords[j][0]
                    lng1 = new_point[1]
                    lng0 = coords[j][1]

                    deglen = 110.25
                    x = lat1 - lat0
                    yy = lng1 - lng0
                    if x < 0.01 and x > -0.01 and yy < 0.05 and yy > -0.05:
                        y = (yy) * math.cos(lat0)
                        if deglen * math.sqrt(x * x + y * y) < 0.5:
                            add = False
                            break
                if add:
                    coords.append(new_point)
                    count += 1

            countOrig += 1
            if countOrig % lines_per_file == 0:
                sys.stdout.write("\33[2K")
                sys.stdout.write("\rTrimmed %d Coordinates to %d" % (countOrig, count))
                sys.stdout.flush()

    coordinates = coordinates + coords
print("")

# Add trimed points to a new file
with open(tmp_dir + "/Travel_Map_Trimmed.csv", mode="w") as outfile:
    outfile.write("Latitude,Longitude\n")
    for pairs in coordinates:
        outfile.write(f"{pairs[0]},{pairs[1]}\n")

# Plot points on an interactive map
mapbox_access_token = "pk.eyJ1IjoianVub3hkIiwiYSI6ImNqeHR4OWE2ZTAyMHIzbXF2bzR4OTB1bGYifQ.QuzCmekFjzCj5tAVAAJFnA"

source = pd.read_csv(tmp_dir + "/Travel_Map_Trimmed.csv")
latitude = source.Latitude
longitude = source.Longitude

data = [
    go.Scattermapbox(
        lat=latitude,
        lon=longitude,
        mode="markers",
        marker=go.scattermapbox.Marker(size=9),
    )
]
layout = go.Layout(
    autosize=True,
    margin={"pad": 0, "l": 0, "r": 0, "t": 0, "b": 0},
    hovermode="closest",
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(lat=45, lon=5),
        pitch=0,
        zoom=1.25,
    ),
)

# FIXME: Remove white outline on HTML
# Center map properly
# Proper sizing for export


outdir = "./Maps/"
outfile = outdir + "Travel-Map-" + datetime.now().strftime("%Y-%m-%d-%s")
latest = "Travel-Map-latest"
if not os.path.exists(outdir):
    os.mkdir(outdir)

# Plot everything
fig = go.Figure(data=data, layout=layout)
py.offline.plot(fig, filename=outfile + ".html")
fig.write_image(outfile + ".png", height=1950, width=2400)

# Update symlink
if os.path.exists(latest + ".html"):
    os.unlink(latest + ".html")
os.symlink(outfile + ".html", latest + ".html")

if os.path.exists(latest + ".png"):
    os.unlink(latest + ".png")
os.symlink(outfile + ".png", latest + ".png")

# Clear the temporary directory
shutil.rmtree(tmp_dir)


# benchmarking
# python3 -m cProfile -o prof.dat 1_split_trim_plot.py
# python3 -m pstats prof.dat
