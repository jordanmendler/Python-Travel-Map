#!/usr/bin/python3

import re
import glob
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
    print("Examples:")
    print("\t./travel_map_plot.py Travel_Map_All.csv ")
    print("\t./travel_map_plot.py ~/Takeout/")
    sys.exit(1)


# Functions
def validCoords(lat, lng):
    if lat < 85 and lat > -60 and lng <= 180 and lng >= -180:
        return True
    else:
        return False


def updateConsole(f, fileCount, numFiles, skipped, invalid, count):
    sys.stdout.write("\33[2K")
    sys.stdout.write(
        "\rProcessed:%d Invalid:%d Skipped:%d\t%s (%d of %d)"
        % (count, invalid, skipped, os.path.basename(f), fileCount, numFiles)
    )


#    sys.stdout.flush()


timestamp = datetime.now().strftime("%Y-%m-%d-%s")

# Split sorted files into smaller files with no more than 10000 lines each
lines_per_file = 10000

# Make a cache directory
tmp_dir = str(tempfile.mkdtemp(".tmp", "travel-map-" + timestamp + "-"))

# Clean and merge input files
files = []

if os.path.isdir(sys.argv[1]):
    files = list(set(files + glob.glob(sys.argv[1] + "/**/*.json", recursive=True)))
    files = list(set(files + glob.glob(sys.argv[1] + "/**/*.kml", recursive=True)))
    files = list(set(files + glob.glob(sys.argv[1] + "/**/*.csv", recursive=True)))
    files = list(set(files + glob.glob(sys.argv[1] + "/*.json")))
    files = list(set(files + glob.glob(sys.argv[1] + "/*.kml")))
    files = list(set(files + glob.glob(sys.argv[1] + "/*.csv")))
else:
    files = glob.glob(sys.argv[1])

with open(tmp_dir + "/1_Travel_Map_Cleaned.csv", mode="w") as outfile:
    writeCSV = csv.writer(outfile, delimiter=",")
    writeInvalidCSV = csv.writer(
        open(tmp_dir + "/1_Travel_Map_Invalid.csv", mode="w"), delimiter=","
    )
    fileCount = 0
    count = 0
    skipped = 0
    invalid = 0

    for f in files:
        fileCount += 1

        with open(f) as infile:
            if ".csv" in f:
                readCSV = csv.reader(infile, delimiter=",")
                for row in readCSV:
                    try:
                        lat = float(row[0])
                        lng = float(row[1])

                        if validCoords(lat, lng):
                            writeCSV.writerow([lat, lng])
                            count += 1
                        else:
                            writeInvalidCSV.writerow([lat, lng, f])
                            invalid += 1
                    except ValueError:
                        skipped += 1
                        print("Invalid on " + f + ":" + row)
                        pass

                    updateConsole(f, fileCount, len(files), skipped, invalid, count)

            elif ".json" in f:
                data = infile.read()

                # Regex Style 1: coordinate pairs
                regex = '"coordinates" : \[ ([+-]?\d+?\.\d+), ([+-]?\d+?\.\d+) \]'
                matches = re.findall(regex, data)
                for match in re.findall(regex, data):
                    try:
                        lng = float(match[0])
                        lat = float(match[1])

                        if validCoords(lat, lng):
                            count += 1
                            writeCSV.writerow([lat, lng])
                        else:
                            writeInvalidCSV.writerow([lat, lng, f])
                            invalid += 1
                    except ValueError:
                        skipped += 1
                        print("Invalid on " + f + ":" + match)
                        pass
                    updateConsole(f, fileCount, len(files), skipped, invalid, count)

                # Regex Style 2: latitude comes first
                data = data.replace("\n", "")
                data = data.replace("\r", "")
                data = data.replace("\t", "")
                data = data.replace(" ", "")
                if data.find("latitude") < data.find("longitude"):
                    regex = '"latitude":([+-]?\d+?\.\d+)\,"longitude":([+-]?\d+?\.\d+)'
                    for match in re.findall(regex, data):
                        try:
                            lat = float(match[0])
                            lng = float(match[1])

                            if validCoords(lat, lng):
                                count += 1
                                writeCSV.writerow([lat, lng])
                            else:
                                writeInvalidCSV.writerow([lat, lng, f])
                                invalid += 1
                        except ValueError:
                            skipped += 1
                            print("Invalid on " + f + ":" + match)
                            pass
                        updateConsole(f, fileCount, len(files), skipped, invalid, count)

                # Regex Style 3: longitude comes first
                else:
                    regex = '"longitude":([+-]?\d+?\.\d+)\,"latitude":([+-]?\d+?\.\d+)'
                    matches = re.findall(regex, data)
                    for match in re.findall(regex, data):
                        try:
                            lng = float(match[0])
                            lat = float(match[1])

                            if validCoords(lat, lng):
                                count += 1
                                writeCSV.writerow([lat, lng])
                            else:
                                writeInvalidCSV.writerow([lat, lng, f])
                                invalid += 1
                        except ValueError:
                            skipped += 1
                            print("Invalid on " + f + ":" + match)
                            pass
                        updateConsole(f, fileCount, len(files), skipped, invalid, count)
            # FIXME: KML still broken based on China.kml
            elif ".kml" in f:
                regex = "([+-]?\d+?\.\d+)[\s\,]([+-]?\d+?\.\d+)[\s\,]\d+"
                for line in infile:
                    for match in re.findall(regex, line):
                        try:
                            lng = float(match[0])
                            lat = float(match[1])

                            if validCoords(lat, lng):
                                count += 1
                                writeCSV.writerow([lat, lng])
                            else:
                                writeInvalidCSV.writerow([lat, lng, f])
                                invalid += 1
                        except ValueError:
                            skipped += 1
                            print("Invalid on " + f + ":" + match)
                            pass
                        updateConsole(f, fileCount, len(files), skipped, invalid, count)
            else:
                print(
                    "Please only in .csv or .json files. Unrecognized filetype for " + f
                )
                sys.exit(1)


# Sort points
# FIXME: This can be merged with prior step
os.system(
    "sort -n "
    + tmp_dir
    + "/1_Travel_Map_Cleaned.csv | uniq > "
    + tmp_dir
    + "/2_Travel_Map_Sorted.csv"
)

# Split into multiple files
my_files = []
with open(tmp_dir + "/2_Travel_Map_Sorted.csv") as infile:
    newfile = None
    for lineno, line in enumerate(infile):
        if lineno >= 0:
            if lineno % lines_per_file == 0:
                if newfile:
                    newfile.close()
                file_num = lineno // lines_per_file + 1
                new_filename = tmp_dir + "/3_Travel_Map_p{}.csv".format(file_num)
                my_files.append(new_filename)
                newfile = open(new_filename, "w")
            newfile.write(line)
    if newfile:
        newfile.close()

# Trim points by density(distance between two closest points)
countOrig = 0
count = 0
coordinates = []
print("")

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
with open(tmp_dir + "/4_Travel_Map_Trimmed.csv", mode="w") as outfile:
    outfile.write("Latitude,Longitude\n")
    for pairs in coordinates:
        outfile.write(f"{pairs[0]},{pairs[1]}\n")

# Plot points on an interactive map
mapbox_access_token = "pk.eyJ1IjoianVub3hkIiwiYSI6ImNqeHR4OWE2ZTAyMHIzbXF2bzR4OTB1bGYifQ.QuzCmekFjzCj5tAVAAJFnA"

source = pd.read_csv(tmp_dir + "/4_Travel_Map_Trimmed.csv")
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
        center=go.layout.mapbox.Center(lat=45, lon=10),
        pitch=0,
        zoom=1.5,
    ),
)

outdir = "./Maps/"
outfile = outdir + "Travel-Map-" + timestamp
latest = "Travel-Map-latest"
if not os.path.exists(outdir):
    os.mkdir(outdir)

# Plot everything
fig = go.Figure(data=data, layout=layout)
py.offline.plot(fig, filename=outfile + ".html")
fig.write_image(outfile + ".small.png", height=1200, width=1450)
fig.write_image(outfile + ".small.square.png", height=1450, width=1450)

fig.write_image(outfile + ".png", height=3600, width=4350)

# Update symlink
if os.path.exists(latest + ".html"):
    os.unlink(latest + ".html")
os.symlink(outfile + ".html", latest + ".html")

if os.path.exists(latest + ".png"):
    os.unlink(latest + ".png")
os.symlink(outfile + ".png", latest + ".png")

# Clear the temporary directory
# shutil.rmtree(tmp_dir)


# benchmarking
# python3 -m cProfile -o /tmp/python.profile ./plot_travel_map.py ~/Takeout/
# python3 -m pstats /tmp/python.profile
